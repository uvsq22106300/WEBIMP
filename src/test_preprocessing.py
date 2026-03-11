from preprocessing import Preprocessor

preprocessor = Preprocessor()

text = preprocessor.load_text("../data/sample.txt")
sentences = preprocessor.split_into_sentences(text)
preprocessor.save_sentences(sentences, "../output/sentences.json")

print("Phrases extraites :")
for sentence in sentences:
    print(sentence)