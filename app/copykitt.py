import os
import re
from typing import List

from openai import OpenAI
import argparse

MAX_INPUT_LENGTH = 32


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", "-i", type=str, required=True)
    args = parser.parse_args()
    user_input = args.input

    print(f"User input: {user_input}")
    if validate_length(user_input):
        generate_branding_snippet(user_input)
        generate_keywords(user_input)
    else:
        raise ValueError(
            f"Input length is too long. Must be under {MAX_INPUT_LENGTH}. Submitted input is {user_input}"
        )


def validate_length(prompt: str) -> bool:
    return len(prompt) <= MAX_INPUT_LENGTH


def generate_keywords(prompt: str) -> List[str]:
    # Load your API key from an environment variable or secret management service
    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    enriched_prompt = f"Generate related branding keywords for {prompt}: "
    print(enriched_prompt)

    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": enriched_prompt,
            }
        ],
        stream=True,
        max_tokens=8,
        model="gpt-4-turbo",
    )
    keywords_text = ''
    # Extract output text.
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            keywords_text += chunk.choices[0].delta.content

    # Strip whitespace.
    keywords_text = keywords_text.strip()
    print(keywords_text)
    keywords_array = re.split(r"\b-\b|\n", keywords_text)
    keywords_array = [k[3::] for k in keywords_array]
    keywords_array = [k.lower().strip() for k in keywords_array]
    keywords_array = [k for k in keywords_array if len(k) > 0]
    print(keywords_array)

    print(f"Keywords: {keywords_array}")
    keywords_string = ", ".join(keywords_array)
    return keywords_array, keywords_string


def generate_branding_snippet(prompt: str):
    # Load your API key from an environment variable or secret management service
    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    enriched_prompt = f"Generate upbeat branding snippet for {prompt}: "
    print(enriched_prompt)

    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": enriched_prompt,
            }
        ],
        max_tokens=16,
        stream=True,
        model="gpt-4-turbo",
    )
    branding_text = ''
    # Extract output text.
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            branding_text += chunk.choices[0].delta.content

    # Strip whitespace.
    branding_text = branding_text.strip()

    # Add ... to truncated statements.
    last_char = branding_text[-1]
    if last_char not in {".", "!", "?"}:
        branding_text += "..."

    print(f"Snippet: {branding_text}")
    return branding_text


if __name__ == '__main__':
    main()
