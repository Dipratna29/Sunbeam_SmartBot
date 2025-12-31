from courses1 import scrape_core_java_course
from courses2 import scrape_python_course
from courses3 import scrape_devops_course
from courses4 import scrape_mern_course
from courses5 import scrape_ml_course
from courses6 import scrape_dsa_java_course
from courses7 import scrape_genai_course
from courses8 import scrape_aptitude_course
from courses9 import scrape_mcqs_course
from courses10 import scrape_spark_course
from courses11 import scrape_mlops_course
from courses12 import scrape_dream_llm_course


def main():

    print("=== Running Core Java Course Scraper ===")
    scrape_core_java_course()
    
    print("\n=== Running Python Course Scraper ===")
    scrape_python_course()

    print("\n=== Running DevOps Course Scraper ===")
    scrape_devops_course()

    print("\n=== MERN Course ===")
    scrape_mern_course()

    print("\n=== Machine Learning Course ===")
    scrape_ml_course()

    print("\n=== DSA Using Java Course ===")
    scrape_dsa_java_course()

    print("\n=== Mastering Generative AI Course ===")
    scrape_genai_course()

    print("\n=== Aptitude Course ===")
    scrape_aptitude_course()

    print("\n=== Mastering MCQs Course ===")
    scrape_mcqs_course()

    print("\n=== Apache Spark Course ===")
    scrape_spark_course()

    print("\n=== MLOps & LLMOps Course ===")
    scrape_mlops_course()

    print("\n=== Dream LLM Course ===")
    scrape_dream_llm_course()


if __name__ == "__main__":
    main()
