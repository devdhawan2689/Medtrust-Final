import openai
import pandas as pd
import re 

# Set your API key
openai.api_key = ""

def get_top_comorbidities(disease_name, top_n=10):
    """
    Fetch top comorbidities for a disease from GPT and return as a DataFrame.

    Args:
        disease_name (str): Name of the disease.
        top_n (int): Maximum number of comorbidities to return (default 10).

    Returns:
        pd.DataFrame: Columns ['Comorbidity', 'Likelihood (%)']
    """
    # Call GPT
    response = openai.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a precise medical data assistant. Respond ONLY with a table of comorbidities "
                    "for the given disease and their percentage likelihoods. No extra text. "
                    "Format: Comorbidity | Likelihood (%)"
                )
            },
            {
                "role": "user",
                "content": f"Provide the top {top_n} comorbidities for {disease_name} with likelihoods in percentage."
            }
        ]
    )

    # Access GPT content
    text = response.choices[0].message.content

    # Process lines
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    # Extract comorbidity and likelihood using robust regex
    rows = []
    for line in lines:
        match = re.match(r"(.+?)\s*\|\s*([\d\.]+)", line)
        if match:
            comorbidity = match.group(1).strip()
            likelihood = float(match.group(2))
            rows.append([comorbidity, likelihood])
        if len(rows) >= top_n:
            break  # Ensure only top N rows

    # Create DataFrame
    df = pd.DataFrame(rows, columns=["Description", "Odds_Ratio"])
    return df

