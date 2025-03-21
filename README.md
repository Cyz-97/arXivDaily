# Daily Repository of Relevant arXiv Papers

This program automatically fetches the latest papers in the fields of **hep-ex** and **hep-ph** from arXiv, analyzes their relevance based on user-defined keywords using one of the supported LLM APIs, and then generates a structured markdown report.
本程序自动从 arXiv 获取 **hep-ex** 和 **hep-ph** 分类下的最新论文，利用指定的 LLM API（支持 ChatGPT、DeepSeek 或 硅基流动）根据用户定义的关键词分析论文的相关性，并生成结构化的 markdown 报告。

The report is saved as a markdown file named with the current date in the format `dailyRepo_{date}.md`.

## Features / 功能
- **Fetch arXiv Papers:** Retrieves the latest papers from arXiv.
  - **获取 arXiv 论文：** 自动从 arXiv 获取最新的论文信息。
- **Evaluate Relevance:** Uses one of the supported APIs (ChatGPT, DeepSeek, or 硅基流动) to determine and explain the paper's relevance to the provided keywords.
  - **评估相关性：** 利用支持的 API（ChatGPT、DeepSeek 或 硅基流动）分析并解释论文与关键词的相关性。
- **Generate Markdown Report:** Organizes the selected papers into a well-structured markdown file.
  - **生成 Markdown 报告：** 将筛选后的论文信息整理成格式化的 markdown 文件。

## Prerequisites / 先决条件
- Python 3.x
- Required Python libraries:
  - `feedparser`
  - `openai`
  - `requests`
  
You can install the required libraries using pip:
可以使用 pip 安装所需的库：
```bash
pip install feedparser openai requests
```


## Setup / 安装步骤
1. **Clone or download this repository.**
   - 克隆或下载本仓库。

2. **Set your API keys and provider.**
   - **API Provider:** Choose which API to use by setting the `API_PROVIDER` environment variable to one of:
     - `chatgpt`
     - `deepseek`
     - `siliconflow`
   - For **ChatGPT**, set the `OPENAI_API_KEY` environment variable.
   - For **DeepSeek**, set the `DEEPSEEK_API_KEY` environment variable (optionally set `DEEPSEEK_API_ENDPOINT` if needed).
   - For **硅基流动**, set the `SILICONFLOW_API_KEY` environment variable (optionally set `SILICONFLOW_API_ENDPOINT` if needed).

   在系统环境变量中设置：
   - `API_PROVIDER`：选择使用的 API（可选值：`chatgpt`、`deepseek`、`siliconflow`）。
   - 对于 **ChatGPT**，设置 `OPENAI_API_KEY`。
   - 对于 **DeepSeek**，设置 `DEEPSEEK_API_KEY`（如有需要可设置 `DEEPSEEK_API_ENDPOINT`）。
   - 对于 **硅基流动**，设置 `SILICONFLOW_API_KEY`（如有需要可设置 `SILICONFLOW_API_ENDPOINT`）。

3. **Edit the keywords.**
   - Open `arXivDaily.py` and modify the `KEYWORDS` variable to include the topics you are interested in.
   - 编辑 `arXivDaily.py` 文件，将 `KEYWORDS` 变量修改为你感兴趣的关键词。

## Running the Program / 运行程序
Simply run the Python script:
直接运行 Python 脚本：

```bash
python arXivDaily.py
```

This will fetch the latest papers, evaluate their relevance using the selected API, and generate a report file named like `dailyRepo_YYYY-MM-DD.md`.
程序将自动获取最新论文，评估相关性，并生成报告文件，文件名格式类似 `dailyRepo_YYYY-MM-DD.md`。

## Scheduling / 定时运行
To run this program automatically every day, you can schedule it using:
如需每天定时运行该程序，可以使用以下方法：
- **Cron (Linux/macOS):**
  - Open your crontab:
    ```
    crontab -e
    ```
  - Add a line to run the script daily at a desired time (e.g., 8 AM):
    ```
    0 8 * * * /usr/bin/python3 /path/to/arXivDaily.py
    ```
- **Task Scheduler (Windows):**
  - Use the Windows Task Scheduler to create a new task that runs `python.exe` with the script path as an argument.

## Notes / 注意事项
- Make sure to adhere to the API rate limits for the selected API.
  - 请注意不要超出所选 API 的调用频率限制。
- The program uses a simple 1-second delay between API calls to help avoid rate limiting.
  - 程序在每次 API 调用之间简单延时 1 秒，以减少因调用频率过快而被限制的可能性。

## License / 许可
This project is provided as-is.
本项目按现状提供，无任何保证。

---

Feel free to modify and extend this project according to your needs.
欢迎根据需要修改和扩展本项目。