#!/usr/bin/env python3
"""
Daily Repository of Relevant arXiv Papers
每日 arXiv 论文筛选程序

This program performs the following tasks:
本程序实现以下功能：
1. Regularly fetches the latest papers from arXiv in the fields of hep-ex and hep-ph.
   定期从 arXiv 获取 hep-ex 和 hep-ph 分类下的最新论文。
2. For each paper, it extracts the title and abstract.
   对每篇论文，提取标题和摘要。
3. Feeds them to an LLM API (ChatGPT, DeepSeek, or 硅基流动) along with user-defined keywords,
   letting the LLM select the papers according to their relevance.
   将论文及用户设置的关键词传递给指定的 LLM API（ChatGPT、DeepSeek 或 “硅基流动”），由 LLM 判断论文相关性。
4. Lists the papers' title, abstract and explains why they are relevant to the interests.
   列出论文标题、摘要以及相关性说明。
5. Organizes them into a structured markdown file, named "dailyRepo_{date}.md".
   生成以当前日期命名（dailyRepo_{日期}.md）的结构化 Markdown 报告。

Required libraries: feedparser, openai, requests.
必需的 Python 库：feedparser, openai, requests。
Install them via pip if needed:
如有需要，可使用 pip 安装：
```
pip install feedparser openai requests
```

Environment variables to set:
需要设置的环境变量：
- OPENAI_API_KEY (for ChatGPT API, if used)
- DEEPSEEK_API_KEY (for DeepSeek API, if used)
- SILICONFLOW_API_KEY (for 硅基流动 API, if used)
- API_PROVIDER (choose one: chatgpt, deepseek, siliconflow)
- Optionally, DEEPSEEK_API_ENDPOINT and SILICONFLOW_API_ENDPOINT can be set.
可选设置 DeepSeek 与 硅基流动 的 API 端点。
"""

import feedparser        # 用于解析 arXiv 的 RSS/Atom feed
import openai            # 用于调用 ChatGPT API
import requests          # 用于调用 DeepSeek 和 硅基流动 API
import os                # 用于环境变量操作
import datetime          # 用于生成日期字符串
import time              # 用于在 API 调用间暂停
import json
import re


# ====================== 配置区域 Configuration ======================

# Set the API provider. 选择使用的 API 提供商（chatgpt、deepseek、siliconflow）
API_PROVIDER = os.getenv("API_PROVIDER", "siliconflow").lower()

# For ChatGPT API, set the OpenAI API key.
# 对于 ChatGPT API，从环境变量中设置 OpenAI API 密钥。
if API_PROVIDER == "chatgpt":
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        raise ValueError(
            "Please set the OPENAI_API_KEY environment variable / 请设置 OPENAI_API_KEY 环境变量")

# Define keywords for relevance filtering.
# 定义用于筛选论文相关性的关键词（请根据你的兴趣修改）。
KEYWORDS = open('interest_summary.txt', 'r', encoding='utf-8').read()  # 请修改为你感兴趣的关键词

# ====================== API 调用函数区域 ======================


def evaluate_paper_relevance_chatgpt(title, abstract, keywords):
    """
    Evaluate paper relevance using ChatGPT API.
    使用 ChatGPT API 评估论文相关性。

    Args:
        title (str): Paper title / 论文标题。
        abstract (str): Paper abstract / 论文摘要。
        keywords (str): User defined keywords / 用户定义的关键词。

    Returns:
        explanation (str): Explanation of relevance.
                           相关性说明。
    """
    prompt = f"""
You are an expert academic researcher.
Below is the title and abstract of a paper:
Title: {title}
Abstract: {abstract}

Given the keywords: "{keywords}", please analyze the paper and explain in detail why it is relevant or not relevant to these keywords.
请扮演一位学术研究专家。
下面是论文的标题和摘要：
标题：{title}
摘要：{abstract}

给定关键词："{keywords}"，请详细分析论文，并解释其为何与这些关键词相关或不相关。
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert academic paper analyzer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            n=1,
            temperature=0.5,
        )
        explanation = response.choices[0].message['content'].strip()
        return explanation
    except Exception as e:
        print(f"Error evaluating paper with ChatGPT: {e}")
        return "Evaluation error using ChatGPT."


def evaluate_paper_relevance_deepseek(title, abstract, keywords):
    """
    Evaluate paper relevance using DeepSeek API.
    使用 DeepSeek API 评估论文相关性。

    Args:
        title (str): Paper title / 论文标题。
        abstract (str): Paper abstract / 论文摘要。
        keywords (str): User defined keywords / 用户定义的关键词。

    Returns:
        explanation (str): Explanation of relevance.
                           相关性说明。
    """
    prompt = f"""
You are an expert academic researcher.
Below is the title and abstract of a paper:
Title: {title}
Abstract: {abstract}

Given the keywords: "{keywords}", please analyze the paper and explain in detail why it is relevant or not relevant to these keywords.
请扮演一位学术研究专家。
下面是论文的标题和摘要：
标题：{title}
摘要：{abstract}

给定关键词："{keywords}"，请详细分析论文，并解释其为何与这些关键词相关或不相关。
    """
    # 获取 DeepSeek API 的端点和密钥
    endpoint = os.getenv("DEEPSEEK_API_ENDPOINT",
                         "https://api.deepseek.ai/v1/chat")
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError(
            "Please set the DEEPSEEK_API_KEY environment variable / 请设置 DEEPSEEK_API_KEY 环境变量")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": prompt,
        "max_tokens": 200,
        "temperature": 0.5
    }
    try:
        response = requests.post(endpoint, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        explanation = result.get("choices", [{}])[0].get("text", "No.").strip()
        return explanation
    except Exception as e:
        print(f"Error evaluating paper with DeepSeek: {e}")
        return "Evaluation error using DeepSeek."


def evaluate_paper_relevance_siliconflow(title, abstract, keywords, repeated=False):
    """
    Evaluate paper relevance using SiliconFlow (硅基流动) API.
    使用硅基流动 API 评估论文相关性。

    Args:
        title (str): Paper title / 论文标题。
        abstract (str): Paper abstract / 论文摘要。
        keywords (str): User defined keywords / 用户定义的关键词。
        repeated (bool): True for first require response;
                         False for seconed repeat,
                         used to avoid infinite recursion.
                       / 是否为第一次要求响应；
                         如果为 False，则表示第二次重复，
                         用于防止无限递归。

    Returns:
        explanation (str): Explanation of relevance.
                           相关性说明。
    """
    prompt = f"""
You are an expert high energy physicist, your are good at academic paper reading and understanding.
Below is the title and abstract of a paper published in arXiv today:
Title: {title}
Abstract: {abstract}

Given:
The user's existing Zotero library, containing titles and abstracts of their collected papers. 
\"\"\"
 {keywords}
\"\"\"
These papers cover a cohesive research trajectory encompassing precision measurements in quantum chromodynamics (QCD), extraction and refinement of the strong coupling constant (αₛ), tau-lepton physics, nonperturbative effects in hadronic decays, particle form factors, searches for dark photons and other exotic particles, as well as detector technologies, specifically with a focus on timing resolution, calorimetry, and advanced machine learning reconstruction methods. 
Recognize that the user's interests form a holistic and continuous research narrative rather than isolated fields.

You will:
1. Approach the comparison by understanding the user's thought process as macroscopic, continuous, and holistic, evaluating how the new arXiv submission integrates into or expands upon their overall research narrative,  explicitly grounded in conceptual alignment, methodological continuity, or thematic complementarity to the user's established research interests.
2. Clearly justify each relevance rating by explicitly referencing how the new work relates to the user's broader academic journey—highlighting common themes, overlapping methodologies, or innovative approaches that resonate with or expand their current research interests.

Your output should only in json format:
{{
    "relevant": float [0-1], 1 for very relevant, 0 for not relevant
    "reason": "Concise and explicit justification tying the arXiv paper to the user's ongoing, integrated research interests, in Chinese."
}}
    """
    # 获取 硅基流动 API 的端点和密钥
    endpoint = os.getenv("SILICONFLOW_API_ENDPOINT",
                         "https://api.siliconflow.cn/v1/chat/completions")
    api_key = os.getenv("SILICONFLOW_API_KEY")
    if not api_key:
        raise ValueError(
            "Please set the SILICONFLOW_API_KEY environment variable / 请设置 SILICONFLOW_API_KEY 环境变量")

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": "Bearer sk-hdenevzwrgofdvhsxxofjjsnmkootiasenmkocsiojxdklvq"
    }
    data = {
        # "model": "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",  # 替换成你的模型
        # "model": "deepseek-ai/DeepSeek-R1-Distill-Llama-8B",  # 替换成你的模型
        # "model": "deepseek-ai/DeepSeek-R1-Distill-Llama-70B", # 替换成你的模型
        "model": "Pro/deepseek-ai/DeepSeek-V3",  # 替换成你的模型
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "max_tokens": 1000,
        "temperature": 0.5
    }
    try:
        response = requests.post(
            endpoint, json=data, headers=headers, stream=False)
        response.raise_for_status()
        print(response)
        result = response.json()
    except Exception as e:
        print(f"Error evaluating paper with SiliconFlow: {e}")
        return e, "-1"

    llm_output = result.get("choices", [{}])[0].get(
        "message", {'role': "", 'content': ""}).get(
        "content", "").strip()

    # Transform the LLM output to a machine-readable format.
    # 将 LLM 输出转换为可机器读取的格式。
    # If transformation fails, repeat the request.
    # 如果转换失败，请重复请求。
    # If the second request fails, return the error.
    # 如果第二次请求失败，则返回错误。
    try:
        remove_markdown = re.sub(r'```json|```', '', llm_output)
        # remove_markdown = re.sub(r'\$(.*?)\$', r'\\[\1\\]', remove_markdown)

        format_output = eval(remove_markdown)
        explanation = format_output.get("reason", "No Explaination.")
        score = str(format_output.get("relevant", "None"))
    except Exception as e:
        print(f"Error when re-formatting output: {e}")
        print(f"llm_output: {llm_output}")
        print(f"remove_markdown: {remove_markdown}")
        print(f"formate_output: {format_output}")
        if (repeated == False):
            print(f"require response from LLM")
            explanation, score = evaluate_paper_relevance_siliconflow(
                title, abstract, keywords, repeated=True)
        else:
            print("This is the seconed time LLM gives wrong output, stop here.")
            return e, "-1"

    return explanation, score


def evaluate_paper_relevance(title, abstract, keywords):
    """
    Evaluate the paper relevance using the selected API provider.
    根据选择的 API 提供商评估论文相关性。

    Args:
        title (str): Paper title / 论文标题。
        abstract (str): Paper abstract / 论文摘要。
        keywords (str): User defined keywords / 用户定义的关键词。

    Returns:
        explanation (str): Explanation of relevance.
                           相关性说明。
    """
    if API_PROVIDER == "chatgpt":
        return evaluate_paper_relevance_chatgpt(title, abstract, keywords)
    elif API_PROVIDER == "deepseek":
        return evaluate_paper_relevance_deepseek(title, abstract, keywords)
    elif API_PROVIDER == "siliconflow":
        return evaluate_paper_relevance_siliconflow(title, abstract, keywords)
    else:
        raise ValueError(
            "Unknown API provider. Please set API_PROVIDER to one of: chatgpt, deepseek, siliconflow.\n未知的 API 提供商，请将 API_PROVIDER 设置为：chatgpt、deepseek 或 siliconflow.")

# ====================== 论文获取与报告生成函数区域 ======================


def fetch_arxiv_papers(arxiv_api_url):
    """
    Fetch papers from the arXiv API.
    从 arXiv API 获取论文数据。

    Returns:
        entries (list): A list of paper entries from arXiv.
                      一个包含 arXiv 论文条目的列表。
    """

    feed = feedparser.parse(arxiv_api_url)
    return feed.entries


def str_to_float(s, default=0.0):
    try:
        return float(s)
    except ValueError:
        return default


def generate_markdown_report(papers_info, report_filename):
    """
    Generate a markdown report with the paper details.
    根据论文信息生成 markdown 格式的报告。

    Args:
        papers_info (list of dict): Each dict contains 'title', 'abstract', and 'explanation'.
                                    每个字典包含论文的 'title'（标题）、'abstract'（摘要）和 'explanation'（相关性说明）。
        report_filename (str): The output markdown file name.
                               输出的 markdown 文件名。
    """
    with open(report_filename, "w", encoding="utf-8") as f:
        # Write header with the current date.
        # 写入包含当前日期的标题。
        f.write(f"# Daily Repository Report - {datetime.date.today()}\n\n")
        for idx, paper in enumerate(papers_info, start=1):
            f.write(f"## Paper {idx}: {paper['title']}\n\n")
            # f.write("**Abstract:**\n")
            # f.write(paper['abstract'] + "\n\n")
            f.write("**Update date:**\n")
            f.write(paper['date'] + "\n\n")
            f.write("**Recommended index:**\n")
            f.write(paper['score'] + "\n\n")
            f.write("**URL:**\n")
            f.write(paper['url'] + "\n\n")
            f.write("**Relevance Explanation:**\n")
            f.write(paper['explanation'] + "\n\n")
            f.write("---\n\n")


def main():
    """
    Main function: fetch papers, evaluate relevance, and generate the markdown report.
    主函数：获取论文，评估相关性，并生成 markdown 报告。
    """

    today = datetime.datetime.now()
    start_date = (today - datetime.timedelta(days=2)).strftime("%Y%m%d")
    end_date = (today - datetime.timedelta(days=0)).strftime("%Y%m%d")

    # Define the arXiv API query URL to fetch hep-ex and hep-ph papers.
    # 定义用于获取 hep-ex 和 hep-ph 论文的 arXiv API 查询 URL。
    arxiv_api_url = (
        "http://export.arxiv.org/api/query?search_query=(cat:hep-ex+OR+cat:hep-ph)+AND"
        f"+submittedDate:%5B{start_date}%20TO%20{end_date}%5D"
        "&start=0&max_results=100&sortBy=submittedDate&sortOrder=descending"
    )
    print("今天是 ", today, "论文起始日期")

    print("Fetching papers from arXiv...")
    print(f"正在从 arXiv 获取 {start_date} 到 {end_date} 的论文...")
    print("API url: ", arxiv_api_url)

    # 重复获取5次数据，直到成功获取文献为止。
    for i in range(5):
        papers = fetch_arxiv_papers(arxiv_api_url)
        if len(papers) != 0:
            break
        else:
            time.sleep(3)

    papers_info = []

    print(
        f"Found {len(papers)} papers. Evaluating relevance using '{API_PROVIDER}' API...")
    print(f"共找到 {len(papers)} 篇论文。使用 '{API_PROVIDER}' API 正在评估相关性...")
    for index, paper in enumerate(papers):
        published_date = datetime.datetime.strptime(
            paper.updated, "%Y-%m-%dT%H:%M:%SZ")

        title = paper.title.replace('\n', ' ')
        # Replace newline characters in abstract for clean formatting.
        # 替换摘要中的换行符以保证格式整洁。
        abstract = paper.summary.replace('\n', ' ')
        print(f"Evaluating paper No. {index}/{len(papers)}: {title}")
        print(f"正在评估第 {index}/{len(papers)} 篇论文：{title}")
        # explanation, score = evaluate_paper_relevance(title, abstract, KEYWORDS)
        explanation, score = evaluate_paper_relevance_siliconflow(
            title, abstract, KEYWORDS)
        papers_info.append({
            "title": title,
            "abstract": abstract,
            "score": score,
            "url": paper.id,
            "date": paper.updated,
            "explanation": explanation
        })
        # Pause to avoid exceeding API rate limits.
        # 暂停1秒以避免 API 调用频率过快的问题。
        time.sleep(1)

    # Sort the papers according to the relevance score.
    # 根据相关性分数对论文进行排序。
    print(papers_info)
    with open('papers_info.json', 'w') as f:
        json.dump(papers_info, f, indent=4)
    if ((papers_info) != 0):
        sorted_list = sorted(
            papers_info, key=lambda x: str_to_float(x['score']), reverse=True)
    else:
        sorted_list = papers_info

    # Create a markdown file named with the current date.
    # 根据当前日期创建 markdown 文件。
    date_str = datetime.date.today().strftime("%Y-%m-%d")
    report_filename = f"share/dailyRepo_{date_str}.md"
    generate_markdown_report(sorted_list, report_filename)
    print(f"Report generated: {report_filename}")
    print(f"报告已生成：{report_filename}")


if __name__ == "__main__":
    main()
