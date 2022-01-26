import cv2

vc = cv2.VideoCapture(1)

rval, frame = vc.read()

while True:

  if frame is not None:
    cv2.imshow("preview", frame)

  rval, frame = vc.read()
  print(rval, frame)

  if cv2.waitKey(1) & 0xFF == ord('q'):
    break

vc.release()
cv2.imshow("output", output)
cv2.waitKey(0)
cv2.destroyAllWindows()
