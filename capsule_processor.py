"""Capsule image processing utilities."""
import os
import re
import cv2 as cv
import numpy as np
import imutils
import matplotlib.pyplot as plt


class CapsuleProcessor:
    """Process capsule images to measure diameter ratios."""

    def __init__(self, image_path: str) -> None:
        """Load image from path.

        Args:
            image_path: Path to the capsule image.
        """
        self.image_path = image_path
        self.image = cv.imread(image_path)
        if self.image is None:
            raise ValueError(f"Unable to load image at {image_path}")

    def angle_rotation(self) -> float:
        """Determine the rotation angle needed to align the capsule."""
        gray = cv.cvtColor(self.image, cv.COLOR_BGR2GRAY)
        mask = cv.adaptiveThreshold(
            gray, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY_INV, 19, 5
        )
        contours, _ = cv.findContours(
            mask.copy(), cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE
        )
        contours = sorted(contours, key=cv.contourArea, reverse=True)
        ellipse_ext = cv.fitEllipse(contours[0])
        canvas = np.zeros_like(gray)
        clean_ellipse = cv.ellipse(canvas, ellipse_ext, (255, 255, 255), 1)
        coords = np.column_stack(np.where(clean_ellipse > 0))
        angle = cv.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        elif angle < 0:
            angle = -angle
        return angle

    def rotate_image(self, angle: float) -> np.ndarray:
        """Rotate the capsule image.

        Args:
            angle: Angle in degrees.

        Returns:
            Rotated image array.
        """
        gray = cv.cvtColor(self.image, cv.COLOR_BGR2GRAY)
        mask = cv.adaptiveThreshold(
            gray, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY_INV, 19, 5
        )
        contours, _ = cv.findContours(
            mask.copy(), cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE
        )
        contours = sorted(contours, key=cv.contourArea, reverse=True)
        if contours:
            contour = max(contours, key=cv.contourArea)
            mask_canvas = np.zeros(gray.shape, dtype="uint8")
            cv.drawContours(mask_canvas, [contour], -1, 255, -1)
            x, y, w, h = cv.boundingRect(contour)
            image_roi = self.image[y : y + h, x : x + w]
            mask_roi = mask_canvas[y : y + h, x : x + w]
            image_roi = cv.bitwise_and(image_roi, image_roi, mask=mask_roi)
            rotated = imutils.rotate_bound(image_roi, angle)
            self.image = rotated
        return self.image

    def measure_pill(self) -> dict:
        """Measure inner and outer diameter ratios of the capsule."""
        angle = self.angle_rotation()
        rotated = self.rotate_image(angle)
        rotated_gray = cv.cvtColor(rotated, cv.COLOR_BGR2GRAY)
        edged = cv.Canny(rotated_gray, 50, 120)
        edged = cv.dilate(edged, None, iterations=1)
        edged = cv.erode(edged, None, iterations=1)
        contours, _ = cv.findContours(
            edged.copy(), cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE
        )
        contours = sorted(contours, key=cv.contourArea, reverse=True)
        x1, y1, w1, h1 = cv.boundingRect(contours[0])
        x2, y2, w2, h2 = cv.boundingRect(contours[1])
        diameters = {
            "outer_contour": sorted([w1, h1], reverse=True),
            "inner_contour": sorted([w2, h2], reverse=True),
        }
        ratio_sup = (
            diameters["inner_contour"][0] / diameters["outer_contour"][0]
        )
        ratio_inf = (
            diameters["inner_contour"][1] / diameters["outer_contour"][1]
        )
        ratio_avg = (ratio_sup + ratio_inf) / 2
        ratios = {
            "ratio_average": ratio_avg,
            "ratio_D": ratio_sup,
            "ratio_d": ratio_inf,
        }
        name = re.split(r"[\\\.,/]", self.image_path)[-2]
        img_copy = rotated.copy()
        plt.rcParams["figure.dpi"] = 150
        ax = plt.gca()
        ax.axes.xaxis.set_ticks([])
        ax.axes.yaxis.set_ticks([])
        plt.imshow(cv.drawContours(img_copy, contours, 0, (255, 0, 0), 1))
        plt.imshow(cv.drawContours(img_copy, contours, 1, (255, 0, 0), 1))
        plt.imshow(
            cv.rectangle(
                img_copy, (x1, y1), (x1 + w1, y1 + h1), (51, 255, 57), 2
            )
        )
        plt.imshow(
            cv.rectangle(
                img_copy, (x2, y2), (x2 + w2, y2 + h2), (51, 255, 57), 2
            )
        )
        plt.title(name)
        output_dir = os.path.join("img_output")
        os.makedirs(output_dir, exist_ok=True)
        plt.savefig(os.path.join(output_dir, f"{name}_output.png"))
        return ratios

    @staticmethod
    def check_parameter(ratios: dict) -> bool:
        """Check if the average ratio is within limits."""
        return 0.3 < ratios["ratio_average"] < 0.7
