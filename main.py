import llm


# ---------------------------------------------- #

GEMINI = llm.Gemini()

# ---------------------------------------------- #
# testing

print(GEMINI.query("how are you doing?"))


# ---------------------------------------------- #
# app

if __name__ == "__main__":
    pass
