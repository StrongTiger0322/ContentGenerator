import json
from openai import OpenAI
client = OpenAI()

def load_config():
	with open('config.json', 'r') as config_file:
		return json.load(config_file)

config = load_config()
GPT_MODEL = config['openai_api']['model']
CONTENT_TOKE = config['openai_api']['content_tokens']
SUMMARY_TOKE = config['openai_api']['summary_tokens']
TEMP = config['openai_api']['temperature']
FILE_EX = config['article_settings']['output_file_extension']

def generate_introduction(heading):
    system_prompt = (
      f"you are a creative introduction writer."
    )
    user_prompt = (
      f"Write a concise introduction with 2~4 sentences, which contains less than 60 words, within the topic '{heading}'."
    )
    response = client.chat.completions.create(
      model=GPT_MODEL,
      max_tokens=CONTENT_TOKE,
      temperature=TEMP,
      messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
      ]
    )
    intro = response.choices[0].message.content
    return intro

def create_content(title, heading, subheading, summary, keywords, guidelines):
  print("-" * 50)
  print(f"Creating content for heading, '{heading}', with subheading titled, '{subheading}'.")

  system_prompt = (
    f"You are a creative content writer. Your content must follow these specific {guidelines}. Use these "
    f"{keywords}, or variations, throughout your content. The title of the content you are writing is, "
    f"'{title}'. Do not repeat information in existing content, here: {summary}."
  )
  user_prompt = (
    f"Write original content for '{subheading}', within the topic '{heading}'. Be original. Be concise. "
    f"Be clear. Do not be repetitive. Don't include the heading and subheading name in the response."
  )

  response = client.chat.completions.create(
    model=GPT_MODEL,
    max_tokens=CONTENT_TOKE,
    temperature=TEMP,
    messages=[
      {"role": "system", "content": system_prompt},
      {"role": "user", "content": user_prompt}
    ]
  )

  content = response.choices[0].message.content

  return content


def summarize_content(content, summary_file='content_summary.txt'):
	response = client.chat.completions.create(
		model=GPT_MODEL,
		max_tokens=SUMMARY_TOKE,
		temperature=TEMP,
		messages=[
			{"role": "system", "content": "You are a content summarizer. Summarize the following content in a concise manner with 20~50 words."},
			{"role": "user", "content": content}
		]
	)
	summary = response.choices[0].message.content

	with open(summary_file, "a") as file:
		file.write(summary + "\n\n")

	print("-" * 50)
	print(summary)
	return summary


def main():
  title = input("Write the title of the eBook you'd like to generate: ")

  with open("table_of_contents.json") as table_of_contents_file:
    toc = json.load(table_of_contents_file)
  with open("keywords.json") as keywords_file:
    keywords = json.load(keywords_file)
  with open("guidelines.json") as guidelines_file:
    guidelines = json.load(guidelines_file)

  for heading, subheads in toc.items():
    with open(f"{title}.{FILE_EX}", "a") as content_file:
      content_file.write(f"<h2>{heading}</h2>\n" \
      f"<p>{generate_introduction(heading)}</p>\n\n")

      for subhead in subheads:
        content_file.write(f"<h3>{subhead}</h3>\n")
        with open('content_summary.txt', 'r', encoding='utf-8', errors='ignore') as summary_file:
          summary = summary_file.read()

        content = create_content(title, heading, subhead, summary, keywords, guidelines)
        summarize_content(content)

        content_file.write(content + "\n\n")

  # print("*" * 50)
  print(f"Completed generating the content titled, '{title}'.")


if __name__ == "__main__":
	main()
