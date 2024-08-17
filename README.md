# Software Interview Agent

This project implements an AI-powered Software Interview Agent using the Anthropic Claude API and LangChain framework. The agent conducts realistic job interviews for software engineering positions, adapting its questions based on the candidate's resume and job description.

## Features

- Conducts multi-stage interviews following a professional structure
- Analyzes candidate resumes and job descriptions to tailor questions
- Maintains conversation history for coherent interactions
- Supports PDF resumes and text-based job descriptions

## Prerequisites

- Python 3.7+
- Anthropic API key

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/software-interview-agent.git
   cd software-interview-agent
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your Anthropic API key as an environment variable:
   ```
   export ANTHROPIC_API_KEY=your_api_key_here
   ```

## Usage

1. Prepare your resume (PDF format) and job description (text format) files.

2. Update the `resume_path` and `job_description_path` variables in the `__main__` section of `agent.py`.

3. Run the interview:
   ```
   python agent.py
   ```

4. Interact with the agent by responding to its questions. Type 'end interview' to conclude the session.

## Customization

You can modify the interview stages, prompts, and other parameters by editing the `SoftwareInterviewAgent` class in `agent.py`.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
