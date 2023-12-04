from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForQuestionAnswering

def answer_question(text, question_line):
# Load the Question Answering pipeline
    model_name = "AIPDF_Reader/trained-model"
    model = AutoModelForQuestionAnswering.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    qa_pipeline = pipeline("question-answering", model=model, tokenizer=tokenizer)

    context = text
    question = question_line

# Use the pipeline to get the answer
    result = qa_pipeline(question=question, context=context)

# Print the answer
    answer = result["answer"]
    print(question)
    print(f"Answer: {answer}")