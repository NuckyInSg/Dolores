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
        self.stats = {"interviewer": 0, "candidate": 0}

    def run_interview(self):
        self.console.print(Panel("Starting the interview...", style="bold green"))

        # Initialize the conversation
        response = self.agent.interview_chain.invoke(
            {"input": "Start the interview with the introduction and small talk stage."},
            config={"configurable": {"session_id": self.session_id}}
        )
        self.display_interviewer_message(response['text'])

        # Main interview loop
        while True:
            answer = self.console.input("[bold cyan]Candidate: [/bold cyan]")
            if answer.lower() == 'end interview':
                break

            self.display_candidate_message(answer)

            response = self.agent.interview_chain.invoke(
                {"input": f"The candidate's response: {answer}\nContinue the interview based on the current stage and the candidate's response."},
                config={"configurable": {"session_id": self.session_id}}
            )
            self.display_interviewer_message(response['text'])

        # Closing remarks
        response = self.agent.interview_chain.invoke(
            {"input": "Provide closing remarks and explain the next steps in the hiring process."},
            config={"configurable": {"session_id": self.session_id}}
        )
        self.display_interviewer_message(response['text'])

        self.display_stats()

    def display_interviewer_message(self, message):
        self.stats["interviewer"] += 1
        extracted_message = self.agent.extract_interviewer_content(message)
        panel = Panel(
            Text(extracted_message),
            title="Interviewer",
            border_style="blue",
            expand=False,
            box=box.ROUNDED
        )
        self.console.print(panel)

    def display_candidate_message(self, message):
        self.stats["candidate"] += 1
        panel = Panel(
            Text(message),
            title="Candidate",
            border_style="green",
            expand=False,
            box=box.ROUNDED
        )
        self.console.print(panel)

    def display_stats(self):
        table = Table(title="Interview Statistics", box=box.DOUBLE_EDGE)
        table.add_column("Participant", style="cyan")
        table.add_column("Messages", style="magenta")
        
        table.add_row("Interviewer", str(self.stats["interviewer"]))
        table.add_row("Candidate", str(self.stats["candidate"]))
        
        self.console.print(table)

if __name__ == "__main__":
    dialog = InterviewDialog()
    dialog.run_interview()