from semantic_router import Route
from semantic_router.routers import SemanticRouter
from semantic_router.encoders import HuggingFaceEncoder

encoder = HuggingFaceEncoder(
    name="sentence-transformers/all-MiniLM-L6-v2"
)


faq = Route(
    name='faq',
    # are the example which will be used to understand these are faq related queries
    utterances=[
        "What is the return policy of the products?",
        "Do I get discount with the HDFC credit card?",
        "How can I track my order?",
        "What payment methods are accepted?",
        "How long does it take to process a refund?",
        "What is your policy on defective product?"
    ]
)

sql = Route(
    name='sql',
    utterances=[
        "I want to buy nike shoes that have 50% discount.",
        "Are there any shoes under Rs. 3000?",
        "Do you have formal shoes in size 9?",
        "Are there any Puma shoes on sale?",
        "What is the price of puma running shoes?",
        "Show top 3 shoes in descending order of rating.",
        "Show top 5 shoes in descending order of rating.",
        "List best-rated shoes.",
        "Show shoes sorted by rating.",
        "Show me top 5 men shirt based on rating",
        "List 5 men shirt ascending on rating",
        "show me worst female shirt",
        "Show me all products in Electronics category",
        "What items do you have in Men's section?",
        "Display all Women's products",
        "List products from Sports category",
        "Show me Jewellery items",
        "What's available in Home appliance category?",
        "Display Computer Accessories",
        "Show me all shoes available",
        "Do you have smartphones in stock?",
        "What keyboards do you sell?",
        "Show me women's jewellery",
        "Display all clothing items",
        "What air conditioners are available?",
        "Show me dumbbells",
        "Show products under 5000 taka",
        "What's the cheapest smartphone?",
        "Display expensive jewellery items",
        "Show shoes under 2000 taka",
        "What's the price range for air conditioners?",
        "Find products between 1000 taka and 3000 tk",
        "Sort smartphones by price",
        "Show best selling products",
        "Display products with 4+ star rating",
        "Show top rated electronics",
        "List the 10 cheapest Men Shoes under 1500 tk",
        "List the 10 cheapest Men Shirts under 2500 tk",
        "Are there any Sports Dumbbells below 2000 tk?",
        "Show Computer Accessories keyboards with 4-star rating and above",
        "show me 5 dumbbells"
    ]
)

unrelated = Route(
    name='unrelated',
    # are the example which will be used to understand these are non healthcare related queries
    utterances=[
        
        # Account and password management
        "How do I reset my account password if I've forgotten it?",
        "How do I reset my account password?",
        "How do I change my username?",
        "How can I update my profile information?",
        "How do I delete my account?",
        
        # Programming and technology
        "How to write a for loop in Python?",
        "How to write for loop in python",
        "What are the best programming languages to learn?",
        "What is machine learning?",
        "Write a for loop in C++",
        "What is blockchain technology?",
        "How do I debug my code?",
        "What is the difference between Python and Java?",
        
        # Travel and booking
        "Can I change my flight date online?",
        "How to book a flight ticket?",
        "What's the cancellation fee for hotel reservations?",
        "How to plan a vacation budget?",
        "What are the best hotels in Paris?",
        
        # Food and restaurants (non-health related)
        "How do I make homemade pasta from scratch?",
        "Do you offer vegan options on the menu?",
        "What are your restaurant opening hours?",
        "How to cook pasta?",
        "What are the best restaurants nearby?",
        "What's the recipe for chocolate cake?",
        
        # Banking and finance
        "How do I view my monthly bank statement?",
        "Can I set up an auto-pay for my credit card bill?",
        "How to invest in stock market?",
        "What is the latest iPhone price?",
        "How do I apply for a credit card?",
        
        # General knowledge and education
        "What is the capital of France?",
        "What's the weather like today?",
        "What are the best movies to watch?",
        "How to learn guitar?",
        "What are the traffic rules for motorcycles?",
        
        # Summary requests (non-medical)
        "Can you summarize this article about technology?",
        "Can you give a summary of today's financial news?",
        "Can you give a summary on data science and AI?",
        "Can you summarize this book?",
        "Can you explain quantum computing?",
        
        # Automotive and mechanical
        "How to fix my car engine?",
        "What's the best car insurance?",
        "How do I change a tire?",
        "What are the signs of engine trouble?",
        
        # Career and professional
        "How to write a resume?",
        "What are good interview questions?",
        "How to negotiate salary?",
        "What skills are needed for data science?"
    ],
)

router = SemanticRouter(routes=[faq,sql,unrelated], encoder=encoder,auto_sync="local")

if __name__ == "__main__":
    print(router("Write a for loop in C++").name)
    print(router("What is your return policy on defective product?").name)
    print(router("Shoes in price range 5000 to 1000").name)
    print(router("Show top 5 shoes in descending order of rating").name)