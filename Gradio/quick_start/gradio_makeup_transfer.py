import os
import torch
import cv2
import os.path as osp
import numpy as np
from PIL import Image
import torchvision.transforms as transforms
import gradio as gr
import colorsys

import CSD_MT_eval  # 내부에 makeup_transfer256 함수가 있음
from color_page_filtering import extract_face_colors, recommend_with_filters, MIN_PRICE, MAX_PRICE


current_mode = "makeup"


def make_color_box(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h / 360, s / 100, v / 100)
    r, g, b = int(r * 255), int(g * 255), int(b * 255)
    hex_color = f'#{r:02X}{g:02X}{b:02X}'
    return f"<div style='width: 100%; height: 24px; background: {hex_color}; border-radius: 6px; border: 1px solid #aaa;'></div>"

def update_s_and_v_previews(h, s, v):
    
    def extract_value(x, default):
        if isinstance(x, dict):
            return x.get("value", default)
        return x if x is not None else default

    h = extract_value(h, 0)
    s = extract_value(s, 100)
    v = extract_value(v, 100)

    try:
        # HSV → RGB로 변환 (범위 변환 포함)
        def to_hex(r, g, b):
            return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

        # Saturation bar: white → 색
        r1, g1, b1 = colorsys.hsv_to_rgb(h/360, 1, v/100)

        c1 = to_hex(r1, g1, b1)
        s_html = f"<div style='height:16px; background: linear-gradient(to right, white, {c1}); border-radius:4px'></div>"

        # Value bar: black → 색
        r2, g2, b2 = colorsys.hsv_to_rgb(h/360, s/100, 1)
        c2 = to_hex(r2, g2, b2)
        v_html = f"<div style='height:16px; background: linear-gradient(to right, black, {c2}); border-radius:4px'></div>"

        return s_html, v_html

    except Exception as e:
        print(f"[!] HSV to RGB 변환 실패: h={h}, s={s}, v={v} → {e}")
        return "", ""


def hsv_to_rgb(h, s, v):
    # h: 0~360, s: 0~100, v: 0~100 → r, g, b: 0~255

    
    # dict 형식이면 내부 value 추출
    if isinstance(h, dict):
        h = h.get("value", 0)
    if isinstance(s, dict):
        s = s.get("value", 0)
    if isinstance(v, dict):
        v = v.get("value", 0)

    h = h / 360
    s = s / 100
    v = v / 100
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return [int(r * 255), int(g * 255), int(b * 255)]

def recommend_by_result_image(result_image, top_n=5):
    lip_hex, _, iris_hex, _, brow_hex, _ = extract_face_colors(result_image)
    lip_title, lip_html = recommend_with_filters(hex_code=lip_hex, sections=[], categories=["lip"], brands=[], types=[], series=[], name_filter="", price_range=(MIN_PRICE, MAX_PRICE), etc_choices=[], top_n=top_n)
    eye_title, eye_html = recommend_with_filters(hex_code=iris_hex, sections=[], categories=["lens"], brands=[], types=[], series=[], name_filter="", price_range=(MIN_PRICE, MAX_PRICE), etc_choices=[], top_n=top_n)
    brow_title, brow_html = recommend_with_filters(hex_code=brow_hex, sections=[], categories=["eyebrow"], brands=[], types=[], series=[], name_filter="", price_range=(MIN_PRICE, MAX_PRICE), etc_choices=[], top_n=top_n)
    return {
        "lip": {"hex": lip_hex, "title": lip_title, "html": lip_html},
        "eye": {"hex": iris_hex, "title": eye_title, "html": eye_html},
        "brow": {"hex": brow_hex, "title": brow_title, "html": brow_html},
    }


def get_makeup_transfer_results256(non_makeup_img, makeup_img, mode,
                                   alpha_eye, alpha_eyebrow, alpha_lip, alpha_all,
                                   regions,
                                   h_eye, s_eye, v_eye,
                                   h_eyebrow, s_eyebrow, v_eyebrow,
                                   h_lip, s_lip, v_lip):
    alpha_values = {
        "eye": alpha_eye,
        "eyebrow": alpha_eyebrow,
        "lip": alpha_lip,
        "all": alpha_all,
    }

    if mode == "makeup":
        img, html = CSD_MT_eval.makeup_transfer256(
            non_makeup_img,
            makeup_img,
            alpha_values,
            regions,
            mode="makeup"
        )
        return img, html
        

    elif mode == "rgb":
        custom_colors = {}
        if "eye" in regions:
            custom_colors["eye"] = hsv_to_rgb(h_eye, s_eye, v_eye)
        if "eyebrow" in regions:
            custom_colors["eyebrow"] = hsv_to_rgb(h_eyebrow, s_eyebrow, v_eyebrow)
        if "lip" in regions:
            custom_colors["lip"] = hsv_to_rgb(h_lip, s_lip, v_lip)

        img, html = CSD_MT_eval.makeup_transfer256(
            non_makeup_img,
            makeup_img,
            alpha_values,
            regions,
            mode="rgb",
            custom_colors=custom_colors
        )
        return img, html



example = {}
non_makeup_dir = 'examples/non_makeup'
makeup_dir = 'examples/makeup'
non_makeup_list = [os.path.join(non_makeup_dir, file) for file in os.listdir(non_makeup_dir)]
non_makeup_list.sort()
makeup_list = [os.path.join(makeup_dir, file) for file in os.listdir(makeup_dir)]
makeup_list.sort()

# Gradio 인터페이스 정의
with gr.Blocks() as demo:
    
    with gr.Group():
        with gr.Tab("CSD-MT"):
            with gr.Row():
                with gr.Column():
                    # === 메이크업 방식 선택 ===
                    makeup_mode = gr.Radio(["makeup", "rgb"], value="makeup", label="Makeup Mode (Choose Source)",
                                           info="Choose 'makeup' for makeup image or 'rgb' for manual color")

                    # 이미지 업로드
                    non_makeup = gr.Image(source='upload', type="numpy", label="Non-makeup Image")
                    gr.Examples(non_makeup_list, inputs=[non_makeup], label="Examples - Non-makeup Image")

                    makeup = gr.Image(source='upload', type="numpy", label="Makeup Image")
                    gr.Examples(makeup_list, inputs=[makeup], label="Examples - Makeup Image")

                with gr.Column():
                    image_out = gr.Image(label="Output", type="numpy").style(height=550)
                    original_image_state = gr.State()


                    
                    # Eye HSV 슬라이더
                    
                    h_eye = gr.Slider(0, 360, value=0, label="Eye Hue (0~360)", visible=False)
                    h_bar = gr.HTML(visible=False)
                    s_eye = gr.Slider(0, 100, value=100, label="Eye Saturation (0~100)", visible=False)
                    s_bar = gr.HTML(visible=False)
                    v_eye = gr.Slider(0, 100, value=100, label="Eye Value (Brightness)", visible=False)
                    v_bar = gr.HTML(visible=False)
                    alpha_eye = gr.Slider(0, 1, value=0.5, step=0.1, label="Eye Alpha", visible=False)

                    
                


                    # Eyebrow HSV 슬라이더
                    h_eyebrow = gr.Slider(0, 360, value=0, label="Eyebrow Hue", visible=False)
                    h_bar_brow = gr.HTML(visible=False)
                    s_eyebrow = gr.Slider(0, 100, value=100, label="Eyebrow Saturation", visible=False)
                    s_bar_brow = gr.HTML(visible=False)
                    v_eyebrow = gr.Slider(0, 100, value=100, label="Eyebrow Brightness", visible=False)
                    v_bar_brow = gr.HTML(visible=False)
                    alpha_eyebrow = gr.Slider(0, 1, value=0.5, step=0.1, label="Eyebrow Alpha", visible=False)



                    # Lip HSV 슬라이더
                    h_lip = gr.Slider(0, 360, value=0, label="Lip Hue", visible=False)
                    h_bar_lip = gr.HTML(visible=False)
                    s_lip = gr.Slider(0, 100, value=100, label="Lip Saturation", visible=False)
                    s_bar_lip = gr.HTML(visible=False)
                    v_lip = gr.Slider(0, 100, value=100, label="Lip Brightness", visible=False)
                    v_bar_lip = gr.HTML(visible=False)
                    alpha_lip = gr.Slider(0, 1, value=0.5, step=0.1, label="Lip Alpha", visible=False)



                    alpha_all = gr.Slider(0, 1, value=0.5, step=0.1, label="Overall Alpha", visible=True)

                    # 체크박스 그룹 (영역 선택)
                    region_selector = gr.CheckboxGroup(
                        ["eye", "eyebrow", "lip", "all"],
                        label="Select Makeup Regions",
                        value=["all"],
                    )

                    
                    btn = gr.Button("Apply Makeup! (CSD-MT)").style()

            with gr.Row():  # ✅ 아래 새 줄
                html_output = gr.HTML(label="Recommended Products (Lip / Eye / Brow)")


            
            def toggle_mode(mode, non_makeup_img):
                global current_mode
                current_mode = mode
                if mode == "makeup":
                    # makeup 모드: HSV 조절 전부 숨김 + region 선택값 초기화
                    return [
                        gr.update(visible=True), gr.update(visible=True), gr.update(visible=True), gr.update(visible=True),
                        *[gr.update(visible=False)] * 18,
                        gr.update(choices=["eye", "eyebrow", "lip", "all"], value=["all"]),
                        gr.update(value=None)  # output 초기화
                    ]
                else:
                    # rgb 모드: HSV 보이고 all 제거됨
                    return [
                        gr.update(visible=True), gr.update(visible=True), gr.update(visible=True), gr.update(visible=False),
                        *[gr.update(visible=True)] * 18,
                        gr.update(choices=["eye", "eyebrow", "lip"], value=[]),
                        gr.update(value=non_makeup_img)  # non-makeup 원본 표시
                    ]

            # toggle_regions 함수 내부에 rgb 모드일 때만 슬라이더 보이도록 제한 추가
            def toggle_regions(selected):

                
                # ✅ makeup 모드일 때: alpha만 보이고 HSV 관련 요소는 숨김
                eye_on = "eye" in selected 
                brow_on = "eyebrow" in selected 
                lip_on = "lip" in selected 
                all_on = "all" in selected

                if current_mode != "rgb":
                    return [
                        gr.update(visible=eye_on, value=0.5 if eye_on else 0),
                        gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False),

                        gr.update(visible=brow_on, value=0.5 if brow_on else 0),
                        gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False),

                        gr.update(visible=lip_on, value=0.5 if lip_on else 0),
                        gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False),

                        gr.update(visible=all_on, value=0.5 if all_on else 0)
                    ]

                return [
                    gr.update(visible=eye_on, value=0.2 if eye_on else 0), gr.update(visible=eye_on, value=0 if not eye_on else gr.update()), gr.update(visible=eye_on), gr.update(visible=eye_on), gr.update(visible=eye_on), gr.update(visible=eye_on), gr.update(visible=eye_on),
                    gr.update(visible=brow_on, value=0.2 if eye_on else 0), gr.update(visible=brow_on, value=0 if not eye_on else gr.update()), gr.update(visible=brow_on), gr.update(visible=brow_on), gr.update(visible=brow_on), gr.update(visible=brow_on), gr.update(visible=brow_on),
                    gr.update(visible=lip_on, value=0.2 if eye_on else 0), gr.update(visible=lip_on, value=0 if not eye_on else gr.update()), gr.update(visible=lip_on), gr.update(visible=lip_on), gr.update(visible=lip_on), gr.update(visible=lip_on), gr.update(visible=lip_on),
                    gr.update(visible=False)
                ]


            # 적용
            makeup_mode.change(
                fn=toggle_mode,
                inputs=[makeup_mode],
                outputs=[
                    alpha_eye, alpha_eyebrow, alpha_lip, alpha_all,
                    h_eye, s_eye, v_eye, h_bar, s_bar, v_bar,
                    h_eyebrow, s_eyebrow, v_eyebrow, h_bar_brow, s_bar_brow, v_bar_brow,
                    h_lip, s_lip, v_lip, h_bar_lip, s_bar_lip, v_bar_lip,
                    region_selector,
                    image_out
                ]
            )


            region_selector.change(
                toggle_regions,
                inputs=[region_selector],
                outputs=[
                    alpha_eye, h_eye, s_eye, v_eye, h_bar, s_bar, v_bar,
                    alpha_eyebrow, h_eyebrow, s_eyebrow, v_eyebrow, h_bar_brow, s_bar_brow, v_bar_brow,
                    alpha_lip, h_lip, s_lip, v_lip, h_bar_lip, s_bar_lip, v_bar_lip,
                    alpha_all
                ]
            )

            h_eye.change(update_s_and_v_previews, inputs=[h_eye, s_eye, v_eye], outputs=[s_bar, v_bar])
            s_eye.change(update_s_and_v_previews, inputs=[h_eye, s_eye, v_eye], outputs=[s_bar, v_bar])
            v_eye.change(update_s_and_v_previews, inputs=[h_eye, s_eye, v_eye], outputs=[s_bar, v_bar])

            h_eyebrow.change(update_s_and_v_previews, inputs=[h_eyebrow, s_eyebrow, v_eyebrow], outputs=[s_bar_brow, v_bar_brow])
            s_eyebrow.change(update_s_and_v_previews, inputs=[h_eyebrow, s_eyebrow, v_eyebrow], outputs=[s_bar_brow, v_bar_brow])
            v_eyebrow.change(update_s_and_v_previews, inputs=[h_eyebrow, s_eyebrow, v_eyebrow], outputs=[s_bar_brow, v_bar_brow])

            h_lip.change(update_s_and_v_previews, inputs=[h_lip, s_lip, v_lip], outputs=[s_bar_lip, v_bar_lip])
            s_lip.change(update_s_and_v_previews, inputs=[h_lip, s_lip, v_lip], outputs=[s_bar_lip, v_bar_lip])
            v_lip.change(update_s_and_v_previews, inputs=[h_lip, s_lip, v_lip], outputs=[s_bar_lip, v_bar_lip])

            btn.click(
                fn=get_makeup_transfer_results256,
                inputs=[
                    non_makeup, makeup, makeup_mode,
                    alpha_eye, alpha_eyebrow, alpha_lip, alpha_all,
                    region_selector,
                    h_eye, s_eye, v_eye,
                    h_eyebrow, s_eyebrow, v_eyebrow,
                    h_lip, s_lip, v_lip
                ],
                outputs = [image_out, html_output]
            )
        

demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))
