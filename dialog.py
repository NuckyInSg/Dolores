import os
from agent import SoftwareInterviewAgent
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box

class InterviewDialog:
    def __init__(self):
        api_key = "my_api_key"
        resume_path = "./docs/local/my_resume.pdf"
        job_description_path = "./docs/local/meta_jd.txt"
        api_url = "https://claude.xinzhang.workers.dev"
        model = "claude-3-5-sonnet"
        self.agent = SoftwareInterviewAgent(api_key, resume_path, job_description_path, model=model, api_url=api_url)
        self.console = Console() 
        self.session_id = "interview_session_1"
        self.stats = {"input": 0, "output": 0, "total": 0}

    def run_interview(self):
        self.console.print("Starting the interview...", style="bold green")

        # Initialize the conversation
        response = self.agent.interview_chain.invoke(
            {"input": "Start the interview with the introduction and small talk stage."},
            config={"configurable": {"session_id": self.session_id}}
        )
        self.display_interviewer_message(response)
        self.update_stats(len("Start the interview with the introduction and small talk stage."), len(response))

        # Main interview loop
        while True:
            answer = self.console.input("[bold cyan]Candidate: [/bold cyan]")
            print("\n")
            if answer.lower() == 'end interview':
                break

            response = self.agent.interview_chain.invoke(
                {"input": f"The candidate's response: {answer}\nContinue the interview based on the current stage and the candidate's response."},
                config={"configurable": {"session_id": self.session_id}}
            )
            self.display_interviewer_message(response)
            self.update_stats(len(answer), len(response))
            # self.display_stats()

        # Closing remarks
        response = self.agent.interview_chain.invoke(
            {"input": "Provide closing remarks and explain the next steps in the hiring process."},
            config={"configurable": {"session_id": self.session_id}}
        )
        self.display_interviewer_message(response)
        self.update_stats(len("Provide closing remarks and explain the next steps in the hiring process."), len(response))
        self.display_stats()

    def display_interviewer_message(self, message):
        extracted_message = self.agent.extract_interviewer_content(message)
        panel = Panel(
            Text(extracted_message, style="cyan"),
            title="Claude's Response",
            subtitle="▼",
            title_align="left",
            border_style="bright_blue",
            expand=False,
            box=box.DOUBLE
        )
        self.console.print(panel)

    def update_stats(self, input_length, output_length):
        self.stats["input"] += input_length
        self.stats["output"] += output_length
        self.stats["total"] = self.stats["input"] + self.stats["output"]

    def display_stats(self):
        table = Table(box=None, show_header=False, show_edge=False, pad_edge=False)
        table.add_column("Stat", style="bold red")
        table.add_column("Value", style="black")
        
        percentage = (self.stats["total"] / 200000) * 100
        cost = (self.stats["total"] / 1000) * 0.01  # 假设每1000个token花费$0.01
        
        table.add_row("Model", "Claude-3-5-sonnet")
        table.add_row("Input", str(self.stats["input"]))
        table.add_row("Output", str(self.stats["output"]))
        table.add_row("Total", str(self.stats["total"]))
        table.add_row("% of Context (200,000)", f"{percentage:.2f}%")
        table.add_row("Cost ($)", f"${cost:.4f}")
        
        panel = Panel(
            table,
            title="Current Statistics",
            title_align="center",
            border_style="white",
            expand=False,
            box=box.DOUBLE
        )
        self.console.print(panel)

if __name__ == "__main__":
    dialog = InterviewDialog()
    dialog.run_interview()