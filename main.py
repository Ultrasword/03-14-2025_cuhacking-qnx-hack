import time
import llm


# ---------------------------------------------- #

GEMINI = llm.Gemini()

# ---------------------------------------------- #
# testing

# result = GEMINI.describe_image("assets/snowyimage.jpg")
# print(result.text)
# result = GEMINI.describe_image_sequence(
#     ["assets/IMG_4173.jpg", "assets/IMG_4174.jpg", "assets/IMG_4175.jpg"]
# )
# print(result.text)
# result = GEMINI.transcript_audio("assets/testaudio.m4a")
# print(result.text)
# result = GEMINI.describe_video("assets/testvideo.mp4")
# print(result.text)


# camera + video saving
import av

print("opening camera io stream")
try:
    input_container = av.open("1", format="avfoundation")
except Exception as e:
    print(e)
    exit()

video_stream = input_container.streams.video[0]
width = video_stream.width
height = video_stream.height

print("opening output stream")
output_container = av.open("assets/output.mp4", "w")
output_stream = output_container.add_stream("libx264", rate=video_stream.rate)
output_stream.width = width
output_stream.height = height
output_stream.pix_fmt = "yuv420p"

start_time = time.time()
duration = 10
frame_count = 0

print("capturing frames")
# capture + encode frames -- this is kinda like a while loop
for frame in input_container.decode(video=0):
    output_container.mux(frame)
    print(f"\r{time.time() - start_time:.2f}", end="")

    packet = output_stream.encode(frame)
    if packet:
        output_container.mux(packet)

    frame_count += 1
    if time.time() - start_time > duration:
        break

print("\nflushing")
# flush any buffered frames
packet = output_stream.encode(None)
if packet:
    output_container.mux(packet)

# close streams
output_container.close()
input_container.close()

print(f"\n{frame_count} frames written to output.mp4")


# ---------------------------------------------- #
# app

if __name__ == "__main__":
    pass
