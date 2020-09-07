import numpy as np
import math
import cv2
from tkinter import *
import tkinter.messagebox

# setari pentru fereastra in care voi avea butoanele de rulare a aplcatiei
root = Tk()
root.geometry('500x450')
frame = Frame(root, relief=RIDGE, borderwidth=5)
frame.pack(fill=BOTH, expand=1)
root.title('Aplicatie de recunoastere a gesturilor mainii')
label = Label()
label.pack(side=TOP)
filename = PhotoImage(file="picture.png")
background_label = Label(frame, image=filename)
background_label.pack(side=TOP)


# functie pentru dechidere camera
def camera():
    capture =cv2.VideoCapture(0)
    while True:
         ret,frame = capture.read()
         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
         frame = cv2.flip(frame, 1)
         cv2.imshow('frame',frame)
         key = cv2.waitKey(1)
         if key == 27:
              break
    capture.release()
    cv2.destroyAllWindows()


# functia principala pentru detectarea gestului
def recunoastere_gest():

    # deschid camera
    capture = cv2.VideoCapture(0)

    # programul ruleaza doar cat timp camera este deschisa
    while capture.isOpened() != 0:

        # iau o captura
        ret, frame = capture.read()

        # oglindesc imaginea
        frame = cv2.flip(frame, 1)

        # definesc regiunea unde voi avea mana in captura
        coord_x = (350, 100)
        coord_y = (550, 300)
        border_color = (0, 255, 0)
        cv2.rectangle(frame, coord_x, coord_y, border_color, 5)

        # salvez regiunea de interes deoarece aici vom prelucra imaginile
        region = frame[100:300, 350:550]

        # transform imaginea din BGR in HSV
        hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)

        # fac o imagine binara pentru a separa mana de fundal
        lower = np.array([0, 50, 50])
        # lower = np.array([5, 0, 0])
        upper = np.array([22, 255, 255])
        mask = cv2.inRange(hsv, lower, upper)

        # declar matrice de 1 pentru dilatare si erodare
        kernel = np.ones((5, 5))

        # fac o dilatare pentru a scapa de zgomotul din imagine
        dilation = cv2.dilate(mask, kernel, iterations=1)

        # fac o erodare pentru a reface imaginea
        erosion = cv2.erode(mask, kernel, iterations=1)

        # aplicam threshold imaginii
        ret, thresh = cv2.threshold(erosion, 127, 255, 0)

        # gasesc contururile mainii
        image, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        try:
            # punctele maxime din contur
            contour = max(contours, key=lambda aux: cv2.contourArea(aux))

            # preiau colturile figurii dreptunghiulare care incadreaza mana
            x, y, w, h = cv2.boundingRect(contour)

            # desenz figura dreptunghiulara din jurul mainii
            cv2.rectangle(region, (x, y), (x + w, y + h), (255, 0, 0), 2)

            #
            hull = cv2.convexHull(contour)

            # desenez contururile pe imagine
            drawing = np.zeros(region.shape, np.uint8)
            cv2.drawContours(drawing, [contour], -1, (0, 255, 0), 0)
            cv2.drawContours(drawing, [hull], -1, (0, 0, 255), 0)

            # aria pentru figura convexa
            area_hull = cv2.contourArea(hull)

            # aria pentru figura dreptunghiulară
            area_contour = cv2.contourArea(contour)

            # gasesc ce procent din figura desenata nu este acoperita de mana
            area_percent = ((area_hull - area_contour) / area_contour) * 100

            # gasesc punctele
            hull = cv2.convexHull(contour, returnPoints=False)

            # posibilele puncte intre degete
            defects = cv2.convexityDefects(contour, hull)

            # cate puncte intre degete
            count_defects = 0

            # gasesc punctele
            for i in range(defects.shape[0]):

                # iau capetele dreptei si cel mai indepartat punct de ea
                s, e, f, d = defects[i, 0]
                start = tuple(contour[s][0])
                end = tuple(contour[e][0])
                farthest = tuple(contour[f][0])

                # calculez unghiul opus dreptei
                a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
                b = math.sqrt((farthest[0] - start[0]) ** 2 + (farthest[1] - start[1]) ** 2)
                c = math.sqrt((end[0] - farthest[0]) ** 2 + (end[1] - farthest[1]) ** 2)

                angle = (math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 180) / 3.14

                semiperimeter = (a + b + c) / 2

                area = math.sqrt(semiperimeter * (semiperimeter - a) * (semiperimeter - b) * (semiperimeter - c))

                # distanta de la punct la marginea figurii
                d = (2 * area) / a

                # daca am un unghi prea mare sau distanta de la cel mai departat punct la dreapta este prea mica,
                # atunci nu iau in calcul
                if angle < 90 and d > 45:
                    count_defects += 1
                    cv2.circle(region, farthest, 3, [255, 255, 255], -1)

                cv2.line(region, start, end, [0, 0, 255], 2)

            # culoarea etxtului
            color = (255, 255, 255)

            # tipul font-ului
            font = cv2.FONT_HERSHEY_SIMPLEX

            # grosimea literei
            thickness = 5

            # dimensinuea fontului
            size = 2

            if count_defects == 0:

                if area_percent < 15:
                    cv2.putText(frame, "PUMN", (240, 50), font, 2, color, 5)
                else:
                    cv2.putText(frame, "UNU", (250, 50), font, 2, color, 5)

            elif count_defects == 1:
                cv2.putText(frame, "DOI", (250, 50), font, 2, color, 5)

            elif count_defects == 2:
                if area_percent < 60:
                    cv2.putText(frame, "OK", (250, 50), font, 2, color, 5)
                else:
                    cv2.putText(frame, "TREI", (250, 50), font, 2, color, 5)

            elif count_defects == 3:
                cv2.putText(frame, "PATRU", (200, 50), font, 2, color, 5)

            elif count_defects == 4:
                cv2.putText(frame, "CINCI", (200, 50), font, 2, color, 5)

            else:
                pass
        except:
            pass

        # afisez imaginea
        cv2.imshow('Frame by frame', frame)

        # la apasarea tastei ESC se termina programul
        key = cv2.waitKey(1)
        if key == 27:
            break

    cv2.destroyAllWindows()
    capture.release()


# functie pentru a inchide fereastra cu butoane
def exitt():
   exit()


# butoanele ce apar in fereastra realizata
buton1 = Button(frame, padx=5, pady=5, width=25, bg='white', fg='black', relief=GROOVE, command=camera, text='Deschide camera video', font=('courier 15 bold'))
buton1.place(x=100, y=104)

buton2 = Button(frame, padx=5, pady=5, width=21, bg='white', fg='black', relief=GROOVE, command=recunoastere_gest, text='Recunoaștere gest', font=('courier 15 bold'))
buton2.place(x=120, y=176)

buton3 = Button(frame, padx=5, pady=5, width=5, bg='white', fg='black', relief=GROOVE, text='EXIT', command=exitt, font=('courier 15 bold'))
buton3.place(x=210, y=330)


root.mainloop()

