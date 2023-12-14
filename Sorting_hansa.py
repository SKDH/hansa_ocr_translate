import cv2
import numpy as np
import math
import json


# 중심 좌표 찾기
def find_center(bboxList):
    for bbox in bboxList:
        x1, y1 = bbox[0][0]
        x3, y3 = bbox[0][2]

        center_x = (x1 + x3) / 2
        center_y = (y1 + y3) / 2

        bbox.insert(-1, [center_x, center_y])
        """
        [[[x1,y1],...,[x4,y4]], [centerx, center_y], 'hansa']
        """
    print("center...ok")
    return bboxList


# 이미지 사이즈 조정 및 좌표값 조정
def resizeImg(img, n=0.2, bboxList=[]):
    h, w = img.shape[:2]

    # 이미지 resize
    image = cv2.resize(img, dsize=(0, 0), fx=n, fy=n)
    nh, nw = image.shape[:2]

    if bboxList:
        # bbox 좌표 resize
        for i, bbox in enumerate(bboxList):
            for j in range(0, 4):
                bbox[0][j][0] = bbox[0][j][0] * nw / w
                bbox[0][j][1] = bbox[0][j][1] * nh / h
            bbox[1][0] = bbox[1][0] * nw / w
            bbox[1][1] = bbox[1][1] * nh / h
            bboxList[i][0] = bbox[0]
        print("resize...ok")

    return image, bboxList


# 이미지 기울기 보정
def imgRotate(img, bboxList):
    sumAngle = 0
    avgAngle = 0

    # 첫번째 좌표와 2번째 좌표의 각도 구하기
    for bbox in bboxList:
        sumAngle += (
            math.atan2(bbox[0][1][1] - bbox[0][0][1], bbox[0][1][0] - bbox[0][0][0])
            * 180.0
            / np.pi
        )
        # print(sumAngle)
    # 구한 각도들의 평균
    avgAngle = sumAngle / len(bboxList)
    # print(avgAngle)

    # 각도 만큼 회전
    (h, w) = img.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, avgAngle, 1.0)
    img = cv2.warpAffine(
        img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
    )

    # 회전한만큼 bbox 수정
    for bbox in bboxList:
        box = np.array(bbox[0], dtype="float32")
        ones = np.ones(shape=(len(box), 1))
        box_ones = np.hstack([box, ones])

        # 회전 적용
        rotated_box = M.dot(box_ones.T).T
        bbox[0] = rotated_box.tolist()

    # 중심좌표 구하기
    bboxList = find_center(bboxList)

    print("tilt...ok")
    return img, bboxList


# 이미지 화면 출력
def imgDraw(img, bboxList):
    if type(bboxList[0]) == type([]):
        for columns in bboxList:
            # 박스 색상 랜덤
            ranColor = (
                np.random.randint(0, 255),
                np.random.randint(0, 255),
                np.random.randint(0, 255),
            )

            for column in columns:
                # 좌표를 numpy 배열로 변환
                pts = np.array(
                    [[column[0][x][0], column[0][x][1]] for x in range(0, 4)],
                    dtype=np.int32,
                )
                pts = pts.reshape((-1, 1, 2))

                # 이미지에 다각형 그리기
                cv2.polylines(
                    img,
                    [pts],
                    True,
                    ranColor,
                )
    elif type(bboxList) == type([]):
        for bbox in bboxList:
            # 좌표를 numpy 배열로 변환
            pts = np.array(
                [[bbox[0][x][0], bbox[0][x][1]] for x in range(0, 4)], dtype=np.int32
            )
            pts = pts.reshape((-1, 1, 2))

            # 이미지에 다각형 그리기
            cv2.polylines(
                img,
                [pts],
                True,
                (0, 255, 0),
            )

            bbox[1][0] = int(bbox[1][0])
            bbox[1][1] = int(bbox[1][1])
            # 이미지에 점 그리기
            cv2.line(img, tuple(bbox[1]), tuple(bbox[1]), (0, 0, 255), 3)
    elif type(bboxList) == type({}) and bboxList["small"]:
        for bbox in bboxList["big"]:
            # 좌표를 numpy 배열로 변환
            pts = np.array(
                [[bbox[0][x][0], bbox[0][x][1]] for x in range(0, 4)], dtype=np.int32
            )
            pts = pts.reshape((-1, 1, 2))

            # 이미지에 다각형 그리기
            cv2.polylines(
                img,
                [pts],
                True,
                (0, 255, 0),
            )

            bbox[1][0] = int(bbox[1][0])
            bbox[1][1] = int(bbox[1][1])
            # 이미지에 점 그리기
            cv2.line(img, tuple(bbox[1]), tuple(bbox[1]), (0, 0, 255), 3)
        for bbox in bboxList["small"]:
            # 좌표를 numpy 배열로 변환
            pts = np.array(
                [[bbox[0][x][0], bbox[0][x][1]] for x in range(0, 4)], dtype=np.int32
            )
            pts = pts.reshape((-1, 1, 2))

            # 이미지에 다각형 그리기
            cv2.polylines(
                img,
                [pts],
                True,
                (255, 0, 0),
            )

            bbox[1][0] = int(bbox[1][0])
            bbox[1][1] = int(bbox[1][1])
            # 이미지에 점 그리기
            cv2.line(img, tuple(bbox[1]), tuple(bbox[1]), (0, 0, 255), 3)

    print("imgshow...ok")
    # cv2.imwrite("testImage3.jpg",img)
    cv2.imshow("Image", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# 열 분리
def separation_of_columns(bboxList):
    boxSumList = []
    boxAvg = 0  # 본분/세주 열 나누는 박스 크기 평균
    boxThreshold = 0  # 열 나누는 문턱값
    twoSize = False

    # 박스크기 평균 및 열 나누는 문턱값 구하기
    for bbox in bboxList:
        w = bbox[0][1][0] - bbox[0][0][0]
        h = bbox[0][3][1] - bbox[0][0][1]
        boxSumList.append(math.sqrt((w * h)))
    boxAvg = sum(boxSumList) / len(bboxList)

    # 이미지내 박스 크기 차이가 적다면 본문과 세주가 섞이지 않은 것으로 간주
    if max(boxSumList) - min(boxSumList) <= 20:
        boxThreshold = boxAvg / 4
    else:
        twoSize = True
        boxThreshold = boxAvg

    columnsList = []
    # 중심좌표 기준으로 열 나누기
    while bboxList:
        subColums = []
        first_box = sorted(bboxList)[0]
        for box in sorted(bboxList):
            """
            [[bbox],[center],'hansa']
            """
            if abs(first_box[1][0] - box[1][0]) <= boxThreshold:
                if twoSize:
                    w = box[0][1][0] - box[0][0][0]
                    h = box[0][3][1] - box[0][0][1]
                    if math.sqrt((w * h)) > boxAvg:
                        box.append('bon')
                    else:
                        box.append('sae')
                subColums.append(box)
        for sub in subColums:
            bboxList.remove(sub)

        columnsList.append(subColums)
    print("separation_of_columns....End")
    return columnsList

# 본문과 세주를 하나의 리스트로 통합
def read_hansa(columnsList):
    def append_sae(saeRight, saeLeft, hansaList):
            hansaList.append('(')
            for sae in saeRight:
                hansaList.append(sae)
            for sae in saeLeft:
                hansaList.append(sae)
            hansaList.append(')')
            
            return hansaList
    hansaAllList = []
    # 중앙 좌표의 x값을 기준으로 내림차순 정렬(오른쪽 부터 읽음)
    sorted_columnsList = sorted(columnsList, key=lambda x: x[1][0] if len(x) > 1 else float('inf'), reverse=True)
    for columns in sorted_columnsList:
        hansaList = []
        saeRight = []
        saeLeft = []
        # 중앙 좌표의 y값을 기준으로 올림차순 정렬(위쪽부터 세로 읽기)
        columns.sort(key=lambda x: x[1][1] if len(x) > 1 else float('inf'))
        i = 0
        while i < len(columns) - 1:
            # 문자가 본문 글자라면
            if columns[i][3] == 'bon':
                if saeRight:
                    hansaList = append_sae(saeRight, saeLeft, hansaList)
                    saeRight = []
                    saeLeft = []
                hansaList.append(columns[i][2])
                i += 1
            # 문자가 세주 글자라면
            else:
                if columns[i+1][3] == 'sae':
                    # 리스트에 들어가있는 문자 순서는 좌우에 다있는 경우로 했는데 가끔 이미지상 한쪽이 비어있는 경우가 있음
                    # 이때 순서가 이상해 지는 걸 중앙 y값 비교로 방지
                    if abs(columns[i][1][1] - columns[i+1][1][1]) <= 10:
                        # 현재 세주문자와 다음 세주문자 간의 중앙 x값 비교, 큰 쪽이 오른쪽 세주
                        if columns[i][1][0] > columns[i+1][1][0]:
                            saeRight.append(columns[i][2])
                            saeLeft.append(columns[i+1][2])
                        else:
                            saeRight.append(columns[i+1][2])
                            saeLeft.append(columns[i][2])
                        i += 2
                    else:
                        saeRight.append(columns[i][2])
                        i += 1
                elif columns[i+1][3] == 'bon':
                    saeRight.append(columns[i][2])
                    i += 1
        if saeRight:
            hansaList = append_sae(saeRight, saeLeft, hansaList)
            saeRight = []
            saeLeft = []
        hansaAllList.append(hansaList)
    return hansaAllList

# 최종 출력
def print_hansa(hansaAllList):
    for hansaList in hansaAllList:
        for hansa in hansaList:
            print(hansa, end="")
        print()

if __name__ == "__main__":
    bboxList = []
    filename = "000000000034277_126"

    with open(f"./EasyOCR/result/{filename}.json", "r", encoding="utf-8") as f:
        json_data = json.load(f)
        for jd in json_data:
            bboxList.append([jd["bbox"], jd["string"]])

    image = cv2.imread(f"./EasyOCR/demo/{filename}.jpg")

    # 이미지 기울기 보정
    # image, bboxList = imgRotate(image, bboxList)
    
    # 중심좌표 생성
    bboxList = find_center(bboxList)

    # 이미지 조절(이미지, 비율값, bbox리스트)
    if image.shape[0] * image.shape[1] > 1980 * 720:
        image, bboxList = resizeImg(image, 0.3, bboxList)

    # 열분리
    columnsList = separation_of_columns(bboxList)
    
    # 하나의 리스트로 통합
    hansaAllList = read_hansa(columnsList)
    print_hansa(hansaAllList)

    # 이미지 화면 출력
    imgDraw(image, columnsList)