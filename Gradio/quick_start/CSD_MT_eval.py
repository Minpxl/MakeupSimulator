import os
import torch
import cv2
import os.path as osp
import numpy as np
from PIL import Image
from CSD_MT.options import Options
from CSD_MT.model import CSD_MT
from faceutils.face_parsing.model import BiSeNet
import torchvision.transforms as transforms
import faceutils as futils
from color_page_filtering import (
    extract_face_colors,
    recommend_with_filters,
    MIN_PRICE,
    MAX_PRICE
)
import warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="torch")

# load face_parsing model
n_classes = 19
face_paseing_model = BiSeNet(n_classes=n_classes)
save_pth = osp.join('faceutils/face_parsing/res/cp', '79999_iter.pth')
face_paseing_model.load_state_dict(torch.load(save_pth,map_location='cpu'))
face_paseing_model.eval()

# load makeup transfer model
parser = Options()
opts = parser.parse()
makeup_model = CSD_MT(opts)
ep0, total_it = makeup_model.resume('CSD_MT/weights/CSD_MT.pth')
makeup_model.eval()




# def crop_image(image):
#     up_ratio = 0.2 / 0.85  # delta_size / face_size
#     down_ratio = 0.15 / 0.85  # delta_size / face_size
#     width_ratio = 0.2 / 0.85  # delta_size / face_size

#     image = Image.fromarray(image)
#     face = futils.dlib.detect(image)

#     if not face:
#         raise ValueError("No face !")

#     face_on_image = face[0]

#     image, face, crop_face = futils.dlib.crop(image, face_on_image, up_ratio, down_ratio, width_ratio)
#     np_image = np.array(image)
#     return np_image

def get_face_parsing(x):
    to_tensor = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
    ])
    with torch.no_grad():
        img = Image.fromarray(x)
        image = img.resize((512, 512), Image.BILINEAR)
        img = to_tensor(image)
        img = torch.unsqueeze(img, 0)
        out = face_paseing_model(img)[0]
        parsing = out.squeeze(0).cpu().numpy().argmax(0)
    return parsing


def extract_skin_color(image, parsing):
    skin_mask = (parsing == 1)
    skin_mask = cv2.resize(skin_mask.astype(np.uint8), (image.shape[1], image.shape[0]), interpolation=cv2.INTER_NEAREST).astype(bool)
    skin_pixels = image[skin_mask]
    if len(skin_pixels) == 0:
        return np.array([0, 0, 0])
    return np.mean(skin_pixels, axis=0)


def refine_eye_mask_by_color(image, eye_mask, skin_color_ref, tolerance=30):
    eye_mask = cv2.resize(eye_mask.astype(np.uint8), (image.shape[1], image.shape[0]), interpolation=cv2.INTER_NEAREST)
    skin_color = np.array(skin_color_ref, dtype=np.float32)
    masked_pixels = image[eye_mask == 1].astype(np.float32)
    distances = np.linalg.norm(masked_pixels - skin_color, axis=1)
    keep_mask = np.zeros_like(eye_mask)
    mask_indices = np.argwhere(eye_mask == 1)
    for idx, dist in zip(mask_indices, distances):
        if dist > tolerance:
            keep_mask[idx[0], idx[1]] = 1
    return keep_mask



def split_parse(opts,parse):
    h, w = parse.shape
    result = np.zeros([h, w, opts.semantic_dim])
    result[:, :, 0][np.where(parse == 0)] = 1
    result[:, :, 0][np.where(parse == 16)] = 1
    result[:, :, 0][np.where(parse == 17)] = 1
    result[:, :, 0][np.where(parse == 18)] = 1
    result[:, :, 0][np.where(parse == 9)] = 1
    result[:, :, 1][np.where(parse == 1)] = 1
    result[:, :, 2][np.where(parse == 2)] = 1
    result[:, :, 2][np.where(parse == 3)] = 1
    result[:, :, 3][np.where(parse == 4)] = 1
    result[:, :, 3][np.where(parse == 5)] = 1
    result[:, :, 1][np.where(parse == 6)] = 1
    result[:, :, 4][np.where(parse == 7)] = 1
    result[:, :, 4][np.where(parse == 8)] = 1
    result[:, :, 5][np.where(parse == 10)] = 1
    result[:, :, 6][np.where(parse == 11)] = 1
    result[:, :, 7][np.where(parse == 12)] = 1
    result[:, :, 8][np.where(parse == 13)] = 1
    result[:, :, 9][np.where(parse == 14)] = 1
    result[:, :, 9][np.where(parse == 15)] = 1
    result = np.array(result)
    return result


def local_masks(opts,split_parse):
    h, w, c = split_parse.shape
    all_mask = np.zeros([h, w])
    all_mask[np.where(split_parse[:, :, 0] == 0)] = 1
    all_mask[np.where(split_parse[:, :, 3] == 1)] = 0
    all_mask[np.where(split_parse[:, :, 6] == 1)] = 0
    all_mask = np.expand_dims(all_mask, axis=2)  # Expansion of the dimension
    all_mask = np.concatenate((all_mask, all_mask, all_mask), axis=2)
    return all_mask



def load_data_from_image(non_makeup_img, makeup_img,opts):
    # non_makeup_img=crop_image(non_makeup_img)
    # makeup_img = crop_image(makeup_img)
    non_makeup_img=cv2.resize(non_makeup_img,(opts.resize_size,opts.resize_size))
    makeup_img = cv2.resize(makeup_img, (opts.resize_size, opts.resize_size))
    non_makeup_parse = get_face_parsing(non_makeup_img)
    non_makeup_parse = cv2.resize(non_makeup_parse, (opts.resize_size, opts.resize_size),interpolation=cv2.INTER_NEAREST)
    makeup_parse = get_face_parsing(makeup_img)
    makeup_parse = cv2.resize(makeup_parse, (opts.resize_size, opts.resize_size),interpolation=cv2.INTER_NEAREST)

    non_makeup_split_parse = split_parse(opts,non_makeup_parse)
    makeup_split_parse = split_parse(opts,makeup_parse)

    non_makeup_all_mask = local_masks(opts,
        non_makeup_split_parse)
    makeup_all_mask = local_masks(opts,
        makeup_split_parse)

    non_makeup_img = non_makeup_img / 127.5 - 1
    non_makeup_img = np.transpose(non_makeup_img, (2, 0, 1))
    non_makeup_split_parse = np.transpose(non_makeup_split_parse, (2, 0, 1))

    makeup_img = makeup_img / 127.5 - 1
    makeup_img = np.transpose(makeup_img, (2, 0, 1))
    makeup_split_parse = np.transpose(makeup_split_parse, (2, 0, 1))

    non_makeup_img=torch.from_numpy(non_makeup_img).type(torch.FloatTensor)
    non_makeup_img = torch.unsqueeze(non_makeup_img, 0)
    non_makeup_split_parse = torch.from_numpy(non_makeup_split_parse).type(torch.FloatTensor)
    non_makeup_split_parse = torch.unsqueeze(non_makeup_split_parse, 0)
    non_makeup_all_mask = np.transpose(non_makeup_all_mask, (2, 0, 1))

    makeup_img = torch.from_numpy(makeup_img).type(torch.FloatTensor)
    makeup_img = torch.unsqueeze(makeup_img, 0)
    makeup_split_parse = torch.from_numpy(makeup_split_parse).type(torch.FloatTensor)
    makeup_split_parse = torch.unsqueeze(makeup_split_parse, 0)
    makeup_all_mask = np.transpose(makeup_all_mask, (2, 0, 1))

    data = {'non_makeup_color_img': non_makeup_img,
            'non_makeup_split_parse':non_makeup_split_parse,
            'non_makeup_all_mask': torch.unsqueeze(torch.from_numpy(non_makeup_all_mask).type(torch.FloatTensor), 0),

            'makeup_color_img': makeup_img,
            'makeup_split_parse': makeup_split_parse,
            'makeup_all_mask': torch.unsqueeze(torch.from_numpy(makeup_all_mask).type(torch.FloatTensor), 0)
            }
    return data


def remove_eye_from_transfer(transfer_img, non_makeup_image, parsing):
    # 눈 마스크 생성 (parsing == 4 또는 5)
    eye_mask = np.zeros_like(parsing, dtype=np.uint8)
    eye_mask[(parsing == 4) | (parsing == 5)] = 1

    # 눈 마스크 확장
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    eye_mask_dilated = cv2.dilate(eye_mask, kernel, iterations=1)

    # 3채널로 확장 및 크기 맞추기
    eye_mask_dilated = cv2.resize(eye_mask_dilated, (transfer_img.shape[1], transfer_img.shape[0]), interpolation=cv2.INTER_NEAREST)
    eye_mask_dilated = np.stack([eye_mask_dilated] * 3, axis=2)

    # non_makeup_image도 크기 맞추기
    non_makeup_resized = cv2.resize(non_makeup_image, (transfer_img.shape[1], transfer_img.shape[0]), interpolation=cv2.INTER_LINEAR)

    # 눈 부분은 non_makeup 이미지로 교체
    cleaned_transfer = transfer_img.copy()
    cleaned_transfer[eye_mask_dilated == 1] = non_makeup_resized[eye_mask_dilated == 1]

    return cleaned_transfer


def extract_eye_mask(parsing, expansion=25, upward_bias=10, inner_bias=20, outer_bias=30):
    """
    눈 영역 마스크를 생성하되,
    - 안쪽(inner): 두 눈 사이 방향으로 확장
    - 바깥쪽(outer): 얼굴 외곽 방향으로 확장
    을 각각 독립적으로 제어할 수 있도록 구현.
    """
    eye_mask = np.zeros_like(parsing, dtype=np.uint8)
    eye_mask[parsing == 4] = 1  # 왼쪽 눈
    eye_mask[parsing == 5] = 1  # 오른쪽 눈

    # 눈 전체 확장
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (expansion, expansion))
    expanded_mask = cv2.dilate(eye_mask, kernel, iterations=1)

    # 위로 확장
    upward_mask = np.zeros_like(expanded_mask)
    upward_mask[:-upward_bias, :] = expanded_mask[upward_bias:, :]

    # 눈 분리
    left_eye_mask = np.where(parsing == 4, expanded_mask, 0)
    right_eye_mask = np.where(parsing == 5, expanded_mask, 0)

    # 왼쪽 눈 - 안쪽 (오른쪽으로 확장)
    left_eye_inner = np.zeros_like(expanded_mask)
    left_eye_inner[:, :-inner_bias] = left_eye_mask[:, inner_bias:]

    # 왼쪽 눈 - 바깥쪽 (왼쪽으로 확장)
    left_eye_outer = np.zeros_like(expanded_mask)
    left_eye_outer[:, outer_bias:] = left_eye_mask[:, :-outer_bias]

    # 오른쪽 눈 - 안쪽 (왼쪽으로 확장)
    right_eye_inner = np.zeros_like(expanded_mask)
    right_eye_inner[:, inner_bias:] = right_eye_mask[:, :-inner_bias]

    # 오른쪽 눈 - 바깥쪽 (오른쪽으로 확장)
    right_eye_outer = np.zeros_like(expanded_mask)
    right_eye_outer[:, :-outer_bias] = right_eye_mask[:, outer_bias:]

    # 모든 마스크 합치기
    final_mask = (
        expanded_mask
        + upward_mask
        + left_eye_inner + left_eye_outer
        + right_eye_inner + right_eye_outer
    )

    # 원래 눈 제거
    final_mask = np.clip(final_mask - eye_mask, 0, 1)
    final_mask[eye_mask == 1] = 0

    return final_mask



def extract_eyebrow_mask(parsing):
    # 눈썹 마스크 생성

    eyebrow_mask = np.zeros_like(parsing, dtype=np.uint8)
    eyebrow_mask[np.where(parsing == 2)] = 1  # 왼쪽 눈썹
    eyebrow_mask[np.where(parsing == 3)] = 1  # 오른쪽 눈썹
    return eyebrow_mask

def extract_lips_mask(parsing):
    # 입술 마스크 생성

    lips_mask = np.zeros_like(parsing, dtype=np.uint8)
    lips_mask[np.where(parsing == 12)] = 1  # 윗입술
    lips_mask[np.where(parsing == 13)] = 1  # 아랫입술
    return lips_mask


def get_face_parsing(x):
    to_tensor = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
    ])
    with torch.no_grad():
        img = Image.fromarray(x)
        image = img.resize((512, 512), Image.BILINEAR)
        img = to_tensor(image)
        img = torch.unsqueeze(img, 0)
        out = face_paseing_model(img)[0]
        parsing = out.squeeze(0).cpu().numpy().argmax(0)
    return parsing


def extract_color_from_mask(image, mask):
    """
    바이너리 마스크(0 또는 1)로부터 해당 영역의 평균 RGB 색상을 추출하여 HEX로 반환
    """
    if image.dtype != np.uint8:
        image = np.clip(image * 255, 0, 255).astype(np.uint8)

    # RGB로 가정
    region_pixels = image[mask.astype(bool)]

    if len(region_pixels) == 0:
        return "#000000"

    avg_color = np.mean(region_pixels, axis=0).astype(np.uint8)
    r, g, b = map(int, avg_color)
    return f'#{r:02X}{g:02X}{b:02X}'


def extract_region_hex_color(image, parsing, region_ids):
    if image.dtype != np.uint8:
        image = np.clip(image * 255, 0, 255).astype(np.uint8)

    parsing_resized = cv2.resize(parsing.astype(np.uint8), (image.shape[1], image.shape[0]), interpolation=cv2.INTER_NEAREST)
    mask = np.isin(parsing_resized, region_ids)

    region_pixels = image[mask]

    if len(region_pixels) == 0:
        return "#000000"

    avg_color = np.mean(region_pixels, axis=0).astype(np.uint8)  # ← image가 RGB라고 가정
    r, g, b = map(int, avg_color)
    return f'#{r:02X}{g:02X}{b:02X}'


def makeup_transfer256(non_makeup_image, makeup_image, alpha_values, regions, mode = "makeup", custom_colors = None):
    import time
    start_time = time.time()

    target_size = (non_makeup_image.shape[1], non_makeup_image.shape[0])

    non_makeup_parse = get_face_parsing(non_makeup_image)
    makeup_parse = get_face_parsing(makeup_image)

    non_makeup_skin = extract_skin_color(non_makeup_image, non_makeup_parse)
    makeup_skin = extract_skin_color(makeup_image, makeup_parse)

    non_makeup_brightness = np.mean(non_makeup_skin)
    makeup_brightness = np.mean(makeup_skin)

    brighter_makeup = makeup_brightness > non_makeup_brightness + 20
    raw_eye_mask = extract_eye_mask(non_makeup_parse)
    refined_eye_mask = refine_eye_mask_by_color(non_makeup_image, raw_eye_mask, non_makeup_skin, tolerance=30)

    masks = {
        "eye": refined_eye_mask,
        "eyebrow": extract_eyebrow_mask(non_makeup_parse),
        "lip": extract_lips_mask(non_makeup_parse),
    }

    data = load_data_from_image(non_makeup_image, makeup_image, opts=opts)
    with torch.no_grad():
        transfer_tensor = makeup_model.test_pair(data)
        transfer_img = transfer_tensor[0].cpu().float().numpy()
        transfer_img = np.transpose((transfer_img / 2 + 0.5) * 255., (1, 2, 0))
        transfer_img = np.clip(transfer_img, 0, 255).astype(np.uint8)
        transfer_img = cv2.resize(transfer_img, target_size, interpolation=cv2.INTER_LINEAR)
        transfer_img = transfer_img.astype(np.float32)

    result_image = non_makeup_image.astype(np.float32)

    if "all" in regions:
        alpha_all = alpha_values.get("all", 1.0)
        all_mask = np.ones(target_size[::-1], dtype=np.float32)

        for region in regions:
            if region != "all" and region in masks:
                m = cv2.resize(masks[region], target_size, interpolation=cv2.INTER_NEAREST)
                m = cv2.GaussianBlur(m.astype(np.float32), (13, 13), 0)
                all_mask = all_mask * (1 - m)

        for c in range(3):
            result_image[:, :, c] = (
                result_image[:, :, c] * (1 - alpha_all * all_mask)
                + transfer_img[:, :, c] * (alpha_all * all_mask)
            )

    for region in [r for r in ["eye", "eyebrow", "lip"] if r in regions]:
        mask = masks.get(region, None)
        if mask is not None:
            mask = cv2.resize(mask, target_size, interpolation=cv2.INTER_NEAREST)
            mask = cv2.GaussianBlur(mask.astype(np.float32), (13, 13), 0)
            mask = mask / mask.max() if mask.max() > 0 else mask

            alpha = alpha_values.get(region, 1.0)

            if mode == "makeup":
                if region == "eye" and brighter_makeup:
                    blend_ratio = 0.4
                    non_makeup_resized = cv2.resize(non_makeup_image, (result_image.shape[1], result_image.shape[0]), interpolation=cv2.INTER_LINEAR).astype(np.float32)
                    for c in range(3):
                        result_image[:, :, c] = (
                            result_image[:, :, c] * (1 - alpha * mask)
                            + (
                                blend_ratio * non_makeup_resized[:, :, c]
                                + (1 - blend_ratio) * transfer_img[:, :, c]
                            ) * (alpha * mask)
                        )
                else:
                    for c in range(3):
                        result_image[:, :, c] = result_image[:, :, c] * (1 - alpha * mask) + transfer_img[:, :, c] * (alpha * mask)

            elif mode == "rgb" and custom_colors is not None and region in custom_colors:
                r, g, b = custom_colors[region]
                for c, val in enumerate([r, g, b]):
                    result_image[:, :, c] = result_image[:, :, c] * (1 - alpha * mask) + val * (alpha * mask)

                non_makeup_resized = cv2.resize(non_makeup_image, (result_image.shape[1], result_image.shape[0]), interpolation=cv2.INTER_LINEAR).astype(np.float32)
                blend_ratio = 0.7
                for c in range(3):
                    result_image[:, :, c] = result_image[:, :, c] * (1 - mask * blend_ratio) + non_makeup_resized[:, :, c] * (mask * blend_ratio)

    result_image = result_image.astype(np.uint8)

    recommendations = recommend_by_result_image_v2(result_image, non_makeup_parse, regions, alpha_values, mode, custom_colors)

    if "lip" in recommendations:
        print("[Lip Recommendation HEX]", recommendations["lip"]["hex"])
        print("[Lip Recommendation HTML]\n", recommendations["lip"]["html"])
    if "eye" in recommendations:
        print("[Eye Recommendation HEX]", recommendations["eye"]["hex"])
        print("[Eye Recommendation HTML]\n", recommendations["eye"]["html"])
    if "eyebrow" in recommendations:
        print("[Brow Recommendation HEX]", recommendations["eyebrow"]["hex"])
        print("[Brow Recommendation HTML]\n", recommendations["eyebrow"]["html"])

    def color_preview(hex_code, label):
        return f"<div style='margin-bottom:8px;'><strong>{label} Color:</strong> <span style='display:inline-block; width:20px; height:20px; background:{hex_code}; border:1px solid #000; margin-left:6px;'></span> {hex_code}</div>"

    color_hex_html = ""
    html_output = ""

    if "lip" in recommendations:
        color_hex_html += color_preview(recommendations["lip"]["hex"], "Lip")
        html_output += recommendations["lip"]["html"]
    if "eye" in recommendations:
        color_hex_html += color_preview(recommendations["eye"]["hex"], "Eye")
        html_output += recommendations["eye"]["html"]
    if "eyebrow" in recommendations:
        color_hex_html += color_preview(recommendations["eyebrow"]["hex"], "Brow")
        html_output += recommendations["eyebrow"]["html"]

    elapsed = time.time() - start_time
    print(f"[INFO] 메이크업 전이 및 추천 완료까지 걸린 시간: {elapsed:.2f}초")
    

    return result_image, color_hex_html + html_output




def recommend_by_result_image_v2(result_image, parsing, regions, alpha_values, mode="makeup", custom_colors=None, top_n=3):

    def compute_weighted_region_hex(image, weighted_mask, mode="makeup", rgb_color=None, skin_color_ref=None,
                                 black_penalty_strength=7, saturation_boost_strength=4):
        
        import colorsys

        def rgb_to_hsv(r, g, b):
            # 0~255 범위 → 0~1 범위로 정규화 후 HSV로 변환
            return colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)


        if image.dtype != np.uint8:
            image = np.clip(image * 255, 0, 255).astype(np.uint8)

        pixels = image[weighted_mask > 0.05]
        if len(pixels) == 0:
            return "#000000"

        pixels = pixels.astype(np.float32)

        # ---------- (1) 검정색 억제 ----------
        black_dist = np.linalg.norm(pixels, axis=1) / np.linalg.norm([255, 255, 255])
        black_weight = black_dist ** black_penalty_strength

        # ---------- (2) 채도 강조 ----------
        pixels_normalized = pixels / 255.0
        hsv_pixels = np.array([rgb_to_hsv(*rgb) for rgb in pixels_normalized])
        saturation = hsv_pixels[:, 1]  # S 채도
        saturation_weight = saturation ** saturation_boost_strength

        # ---------- (3) 가중치 통합 ----------
        combined_weight = black_weight * saturation_weight + 1e-6
        combined_weight /= np.sum(combined_weight)

        # ---------- (4) 평균 계산 ----------
        if mode == "makeup":
            if skin_color_ref is not None:
                distances = np.linalg.norm(pixels - np.array(skin_color_ref), axis=1)
                combined_weight *= distances + 1e-6
                combined_weight /= np.sum(combined_weight)
        elif mode == "rgb" and rgb_color is not None:
            pixels = np.array(rgb_color, dtype=np.float32).reshape(1, 3).repeat(len(pixels), axis=0)

        weighted_avg = np.sum(pixels * combined_weight[:, np.newaxis], axis=0)

        r, g, b = weighted_avg.astype(np.uint8)
        return f'#{r:02X}{g:02X}{b:02X}'


    results = {}
    for region in [r for r in ["lip", "eye", "eyebrow"] if ("all" in regions or r in regions)]:
        alpha = alpha_values.get(region, 1.0)
        mask = get_weighted_mask(region, parsing, result_image.shape[:2])
        non_makeup_skin = extract_skin_color(result_image, parsing)

        if mask is None:
            continue

        if mode == "rgb" and custom_colors and region in custom_colors:
            hex_color = compute_weighted_region_hex(result_image, mask * alpha, mode="rgb", rgb_color=custom_colors[region]if mode=="rgb" else None,
                                        skin_color_ref=non_makeup_skin)
        else:
            hex_color = compute_weighted_region_hex(result_image, mask * alpha, mode="makeup")

        section_map = {
            "lip": (["lip"], [], [], [], []),
            "eye": ([], ["eye shadow"], [], [], []),
            "eyebrow": ([], ["eyebrow"], [], [], [])
        }
        sections, categories, brands, types, series = section_map[region]

        title, html = recommend_with_filters(
            hex_code=hex_color,
            sections=sections, categories=categories, brands=brands,
            types=types, series=series,
            name_filter="", price_range=(MIN_PRICE, MAX_PRICE), etc_choices=[], top_n=top_n
        )

        results[region] = {"hex": hex_color, "title": title, "html": html}

    return results

def get_weighted_mask(region_name, parsing, target_size):
    if region_name == "eye":
        raw_mask = extract_eye_mask(parsing, expansion=20, upward_bias=5, inner_bias=5, outer_bias=10)
    elif region_name == "eyebrow":
        raw_mask = extract_eyebrow_mask(parsing)
    elif region_name == "lip":
        raw_mask = extract_lips_mask(parsing)
    else:
        return None

    mask = cv2.resize(raw_mask, target_size[::-1], interpolation=cv2.INTER_NEAREST).astype(np.float32)
    mask = cv2.GaussianBlur(mask, (5,5), 0)
    return mask / mask.max() if mask.max() > 0 else mask
