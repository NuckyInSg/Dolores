import os
from agent import SoftwareInterviewAgent
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box

class InterviewDialog:
    def __init__(self, api_key, resume_path,
                 job_description_path, model, api_url=None):
        self.api_key = api_key
        self.api_url = api_url or os.getenv("ANTHROPIC_API_URL") or "https://api.anthropic.com"
        self.resume_path = resume_path
        self.job_description_path = job_description_path
        self.model = model

        self.agent = SoftwareInterviewAgent(self.api_key, self.resume_path, self.job_description_path, 
                                            model=self.model, api_url=self.api_url)
        self.console = Console() 
        self.session_id = "interview_session_1"
        self.stats = {"input": 0, "output": 0, "total": 0}
        self.commands = {
            "/info": self.display_stats,
            "/save": self.save_interview,
            "/exit": self.exit_interview,
        }
        self.chat_history = []  # Initialize chat_history

    def run_interview(self):
        self.console.print("Starting the interview...", style="bold green")

        # Initialize the conversation
        response = self.agent.interview_chain.invoke(
            {"input": "Start the interview with the introduction and small talk stage."},
            config={"configurable": {"session_id": self.session_id}}
        )
        self.display_interviewer_message(response)
        self.update_stats(len("Start the interview with the introduction and small talk stage."), len(response))
        self.chat_history.append({"role": "ai", "content": response})  # Add this line

        # Main interview loop
        while True:
            answer = self.console.input("[bold cyan]Candidate: [/bold cyan]")
            print("\n")
            
            if answer.startswith('/'):
                self.handle_command(answer)
                continue

            self.chat_history.append({"role": "human", "content": answer})  # Add this line

            response = self.agent.interview_chain.invoke(
                {"input": f"The candidate's response: {answer}\nContinue the interview based on the current stage and the candidate's response."},
                config={"configurable": {"session_id": self.session_id}}
            )
            self.display_interviewer_message(response)
            self.update_stats(len(answer), len(response))
            self.chat_history.append({"role": "ai", "content": response})  # Add this line

        # Closing remarks
        response = self.agent.interview_chain.invoke(
            {"input": "Provide closing remarks and explain the next steps in the hiring process."},
            config={"configurable": {"session_id": self.session_id}}
        )
        self.display_interviewer_message(response)
        self.update_stats(len("Provide closing remarks and explain the next steps in the hiring process."), len(response))
        self.display_stats()

    def handle_command(self, command):
        cmd = command.lower().strip()
        if cmd in self.commands:
            self.commands[cmd]()
        else:
            self.console.print(f"Unknown command: {command}", style="bold red")
        

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

    def save_interview(self):
        filename = f"interview_{self.session_id}.md"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write("# Software Engineering Interview\n\n")
            
            for entry in self.chat_history:
                if entry["role"] == "human":
                    f.write(f"## Candidate\n\n{entry['content']}\n\n")
                elif entry["role"] == "ai":
                    f.write(f"## Interviewer\n\n{self.agent.extract_interviewer_content(entry['content'])}\n\n")
            
            f.write("## Interview Statistics\n\n")
            f.write(f"- Total tokens: {self.stats['total']}\n")
            f.write(f"- Input tokens: {self.stats['input']}\n")
            f.write(f"- Output tokens: {self.stats['output']}\n")
            f.write(f"- Percentage of context used: {(self.stats['total'] / 200000) * 100:.2f}%\n")
            f.write(f"- Estimated cost: ${(self.stats['total'] / 1000) * 0.01:.4f}\n")
        
        self.console.print(f"Interview saved as [bold green]{filename}[/bold green]")


    def exit_interview(self):
        self.console.print("Exiting the interview...", style="bold red")
        exit()

if __name__ == "__main__":
    api_key = os.getenv("ANTHROPIC_API_KEY")
    api_url = os.getenv("ANTHROPIC_API_URL")
    resume_path = "./docs/local/resume.pdf"
    job_description_path = "./docs/local/job_description.txt"
    model = "claude-3-5-sonnet"
    dialog = InterviewDialog(api_key=api_key, 
                             api_url=api_url, 
                             resume_path=resume_path, 
                             job_description_path=job_description_path, 
                             model=model)
    dialog.run_interview()