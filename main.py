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
result = GEMINI.transcript_audio("assets/testaudio.m4a")
print(result.text)


# ---------------------------------------------- #
# app

if __name__ == "__main__":
    pass
