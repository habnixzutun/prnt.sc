import os
import tkinter.messagebox
import requests
from bs4 import BeautifulSoup
from tkinter import *
from PIL import Image, ImageTk
import io
import random
import subprocess
from hashlib import sha1
import webbrowser
from threading import Thread
from time import sleep


headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip,deflate, br, zstd",
    "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "max-age=0",
    "Cookie": "_gid=GA1.2.572765023.1745443014; _ga=GA1.1.1596534634.1745443014; _ga_STH272KG8X=GS1.1.1745443013.1.1.1745443027.0.0.0",
    "Priority": "u=0, i",
    "Sec-Ch-Ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Platform": "Windows",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
}

headers_img = {
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    "Accept-Encoding": "gzip,deflate, br, zstd",
    "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "max-age=0",
    "Cookie": "_gid=GA1.2.572765023.1745443014; _ga=GA1.1.1596534634.1745443014; _ga_STH272KG8X=GS1.1.1745443013.1.1.1745443027.0.0.0",
    "Priority": "u=0, i",
    "Sec-Ch-Ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Platform": "Windows",
    "Referrer": "https://prnt.sc/",
    "Sec-Fetch-Dest": "image",
    "Sec-Fetch-Mode": "no-cors",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-Storage-Access": "active",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
}


CURRENT_IMAGE = dict()
NEXT_IMAGES = list()  # lists of dicts
PREV_IMAGES = list()
ALREADY_CHECKED = list()
KYS = False

FONT = ("Calibri", 12)


def get_image(img_id):
    site = requests.get(f"https://prnt.sc/{img_id}", headers=headers)
    if not site.ok:
        return
    soup = BeautifulSoup(site.text, parser="html", features="lxml")
    img_src = soup.find("img")
    if not img_src:
        return
    img_src = img_src["src"]
    if not img_src.startswith("https://"):
        if img_src.startswith("//"):
            img_src = "https:" + img_src
        else:
            img_src = "https://" + img_src
    if soup.find("img").get("image-id") != img_id:
        return
    img = requests.get(img_src, headers=headers_img)
    if not img.ok:
        return
    if sha1(img.content).hexdigest() == "20002faf28adfd94ca98cf6ced46f14334b53684":
        return
    if sha1(img.content).hexdigest() == "55d461ab54ac62a5abcc654a568173b483ec498e":
        return
    if sha1(img.content).hexdigest() == "342003b685eb85850a0dd5637b8ac3274d415af1":  # Telegram
        return
    if sha1(img.content).hexdigest() == '3920004e0c02dfcf610c0ac89c3b858407fa0b11':  # Achim
        return
    print(img_id, sha1(img.content).hexdigest())
    return img_id, img_src, img.content


def save_image():
    with open(f"{CURRENT_IMAGE['img_id']}.png", "wb") as f:
        f.write(CURRENT_IMAGE["original"])


def open_folder():
    path = os.getcwd()
    try:
        if os.name == "posix":
            subprocess.Popen(['xdg-open', path])
        if os.name == "nt":
            subprocess.Popen(['explorer', path])
    except FileNotFoundError:
        tkinter.messagebox.Message(title="Info", message="OS not supported").show()


def open_browser():
    global CURRENT_IMAGE
    global NEXT_IMAGES
    global PREV_IMAGES
    webbrowser.open("https://prnt.sc/" + CURRENT_IMAGE["img_id"])


def back(window, label):
    global CURRENT_IMAGE
    global NEXT_IMAGES
    global PREV_IMAGES

    if PREV_IMAGES == [{}]:
        tkinter.messagebox.Message(message="There is no previous image", title="Info").show()
        return
    NEXT_IMAGES = [CURRENT_IMAGE, *NEXT_IMAGES]
    CURRENT_IMAGE = PREV_IMAGES[-1]
    PREV_IMAGES.pop(len(PREV_IMAGES) - 1)
    img_id = CURRENT_IMAGE["img_id"]
    img_resized_bytes = CURRENT_IMAGE["resized"]
    windows_geometry = CURRENT_IMAGE["window_geometry"]
    window.title(f"prnt.sc/{img_id}")
    window.geometry(windows_geometry)
    tkimg = ImageTk.PhotoImage(img_resized_bytes)
    label.configure(image=tkimg)
    label.image = tkimg
    """img_id = window.title()[8:]
    if IMG_HISTORY and not img_id == IMG_HISTORY[0]:
        regenerate(window, label, img_id=IMG_HISTORY[IMG_HISTORY.index(img_id) - 1])
    else:
        tkinter.messagebox.Message(message="There is no previous image", title="Info").show()"""


def next(window, label):
    global CURRENT_IMAGE
    global NEXT_IMAGES
    global PREV_IMAGES
    PREV_IMAGES.append(CURRENT_IMAGE)
    if len(PREV_IMAGES) > 110:
        PREV_IMAGES = PREV_IMAGES[10:]
    while not NEXT_IMAGES:
        sleep(1/120)
    CURRENT_IMAGE = NEXT_IMAGES[0]
    NEXT_IMAGES.pop(0)
    img_id = CURRENT_IMAGE["img_id"]
    img_resized_bytes = CURRENT_IMAGE["resized"]
    windows_geometry = CURRENT_IMAGE["window_geometry"]
    window.title(f"prnt.sc/{img_id}")
    window.geometry(windows_geometry)
    tkimg = ImageTk.PhotoImage(img_resized_bytes)
    label.configure(image=tkimg)
    label.image = tkimg


def regenerate():
    global NEXT_IMAGES
    global PREV_IMAGES
    while True:
        while len(NEXT_IMAGES) >= 50 and not KYS:
            sleep(5)
        image = None
        img_id = ""
        while image is None:
            while img_id in ALREADY_CHECKED:
                img_id = ""
                for i in range(6):
                    img_id += chr(random.choice([*range(48, 58), *range(97, 121)]))
            raw = get_image(img_id)
            ALREADY_CHECKED.append(img_id)
            if raw is not None:
                image = raw[-1]
            if KYS:
                return
        img_infos = Image.open(io.BytesIO(image))
        img_original = image
        width = img_infos.width
        height = img_infos.height + 50
        max_width = 1600
        min_width = 415
        max_height = 800
        print((width, height))
        if width <= 0 or img_infos.height <= 0:
            continue
        if width / height > 16 / 9 and width > max_width:
            img_infos = img_infos.resize((max_width, int(round(max_width / (width / height)))))
        if width / height < 16 / 9 and height > max_height:
            img_infos = img_infos.resize((int(round(max_height / (height / width))), max_height))
        if width < min_width:
            window_geometry = f"{min_width}x{height}"
        else:
            window_geometry = f"{img_infos.width}x{img_infos.height + 50}"

        NEXT_IMAGES.append({
            "img_id": img_id,
            "original": img_original,
            "resized": img_infos,
            "window_geometry": window_geometry
        })


def start_threads(amount=3):
    [Thread(target=regenerate).start() for _ in range(amount)]


if __name__ == '__main__':
    if not os.path.isdir("imgs"):
        os.mkdir("imgs")
    os.chdir("imgs")

    start_threads()

    root = Tk()

    panel = Label(root, image="")
    panel.grid(row=0, column=0, columnspan=5)

    back_button = Button(root, text="Back", font=FONT, command=lambda: back(root, panel))
    back_button.grid(row=1, column=0, sticky="w", padx=(3, 0))

    save_button = Button(root, text="Save Image", font=FONT, command=save_image)
    save_button.grid(row=1, column=1)

    folder_button = Button(root, text="Open Folder", font=FONT, command=open_folder)
    folder_button.grid(row=1, column=2)

    browser_button = Button(root, text="Open Browser", font=FONT, command=open_browser)
    browser_button.grid(row=1, column=3)

    regenerate_button = Button(root, text="Next", font=FONT, command=lambda: next(root, panel))
    regenerate_button.grid(row=1, column=4, sticky="e", padx=(0, 7))

    next(root, panel)

    root.mainloop()

    KYS = True
