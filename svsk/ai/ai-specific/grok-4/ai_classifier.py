# AI Statement Classifier - Micro App for ARTI Education
# Task: Classify AI-related statements as 'Opportunity', 'Risk', or 'Neutral' using keyword-based technique
# Inspired by ARTI Level 1: Simple classification, ethical dilemmas, opportunities/risks of AI
# Usage: Run the script, input statements, discuss outputs in class

def classify_ai_statement(statement):
    """
    Classify the statement based on keyword counts.
    Opportunity keywords: From curriculum themes like improvement, enhancement.
    Risk keywords: From themes like concerns, biases, consequences.
    """
    # Keywords derived from ARTI curriculum (opportunities vs. risks/ethics)
    opportunity_keywords = ["improve", "enhance", "enable", "better", "contribute", "development", "possibilities", "opportunities"]
    risk_keywords = ["risk", "concern", "dilemma", "bias", "consequence", "ethical", "security", "transparency"]
    
    # Count matches (case-insensitive)
    opp_count = sum(1 for kw in opportunity_keywords if kw in statement.lower())
    risk_count = sum(1 for kw in risk_keywords if kw in statement.lower())
    
    if opp_count > risk_count:
        return "Opportunity"
    elif risk_count > opp_count:
        return "Risk"
    else:
        return "Neutral"

def main():
    print("AI Statement Classifier - ARTI Education Demo")
    print("Enter AI-related statements (e.g., 'AI can improve healthcare'). Type 'quit' to exit.")
    print("Discuss: How does this simple keyword classifier compare to human judgment?")
    
    while True:
        statement = input("\nStatement: ")
        if statement.lower() == 'quit':
            break
        classification = classify_ai_statement(statement)
        print(f"Classification: {classification}")

if __name__ == "__main__":
    main()
