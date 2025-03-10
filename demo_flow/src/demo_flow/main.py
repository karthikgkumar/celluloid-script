#!/usr/bin/env python
import asyncio
from random import randint
from pydantic import BaseModel
from typing import List
from crewai.flow import Flow, listen, start
from src.demo_flow.crews.outline_crew.outline_crew import OutlineCrew
from src.demo_flow.script_types import Chapter, ChapterOutline
from src.demo_flow.crews.write_script.write_script import WriteScript
class ScriptState(BaseModel):
    title: str = ("Ethan's investigation")
    genre: str = (
        "Investigation Thriller"
    )
    book: List[Chapter] = []
    book_outline : List[ChapterOutline] = []
    logline: str= ("A troubled investigative journalist must navigate a web of corporate corruption and personal demons to expose a powerful businessman's murderous secret before more lives are lost.")
    central_message: str= """
    The pursuit of truth requires confronting both external corruption and internal darkness.
    """
    main_character_profiles: str = """
    Name: Ethan Cole Age: 35 Occupation: Investigative Journalist
    Personality: Intelligent, obsessive, morally conflicted
    Background: Ethan grew up in a rough neighborhood, using his sharp mind to escape 
                a life of crime. He gained fame for uncovering high-profile scandals 
                but struggles with past trauma and a drinking problem.
    Motivation: Determined to expose corruption, but haunted by a past case that went 
                horribly wrong.
    Character Arc: Ethan starts as a lone wolf who trusts no one, but through his 
                  latest case, he learns the value of connection and truth over 
                  sensationalism.
    Flaws: Stubborn, reckless, prone to self-destruction.
    Strengths: Sharp intuition, relentless pursuit of the truth.
    """
    supporting_charcter_profiles : str = """
    1. Dr. Lillian Graves (Psychologist, 40s)
       - Ethan's therapist, intelligent but emotionally guarded
       - She holds a secret about Ethan's past that could break him

    2. Marcus "Mack" DeLuca (Cop, 50s)
       - Ethan's reluctant ally, a veteran detective who has seen too much
       - He helps Ethan navigate the criminal underworld but warns him not to push too far

    3. Sophia Reyes (Tech Specialist, 28)
       - A hacker who helps Ethan dig into classified files
       - Sarcastic, street-smart, and secretly on the run from her own past

    4. Vincent Kane (Antagonist, 45)
       - A powerful businessman hiding a dark secret
       - He manipulates the media and law enforcement to cover up crimes
    """
    abstract: str= """
    A gritty investigative thriller about a journalist who uncovers a conspiracy involving corporate corruption and murder, forcing him 
    to confront his own demons while pursuing the truth.
    """


class PoemFlow(Flow[ScriptState]):

    @start()
    def generate_book_outline(self):
        print("Kickoff the Book Outline Crew")
        output = (
            OutlineCrew()
            .crew()
            .kickoff(inputs={"genre": self.state.genre, "logline": self.state.logline
                             , "abstract": self.state.abstract,
                             "main_character_profiles": self.state.main_character_profiles,
                             "side_character_profiles": self.state.supporting_charcter_profiles,
                             "central_message": self.state.central_message,
                             "title": self.state.title
                             })
        )

        chapters = output["chapters"]
        print("Chapters:", chapters)

        self.state.book_outline = chapters

    @listen(generate_book_outline)
    async def write_chapters(self):
        print("Writing Scenes")
        tasks = []

        async def write_single_chapter(chapter_outline):
            output = (
                WriteScript()
                .crew()
                .kickoff(
                    inputs={
                        "genre": self.state.genre,
                        "logline": self.state.logline,
                        "abstract": self.state.abstract,
                        "main_character_profiles": self.state.main_character_profiles,
                        "side_character_profiles": self.state.supporting_charcter_profiles,
                        "central_message": self.state.central_message,
                        "chapter_title": chapter_outline.title,
                        "chapter_description": chapter_outline.description,
                        "book_outline": [
                            chapter_outline.model_dump_json()
                            for chapter_outline in self.state.book_outline
                        ],
                        "title": self.state.title
                    }
                )
            )
            title = output["title"]
            content = output["content"]
            chapter = Chapter(title=title, content=content)
            return chapter

        for chapter_outline in self.state.book_outline:
            print(f"Writing Chapter: {chapter_outline.title}")
            print(f"Description: {chapter_outline.description}")
            # Schedule each chapter writing task
            task = asyncio.create_task(write_single_chapter(chapter_outline))
            tasks.append(task)

        # Await all chapter writing tasks concurrently
        chapters = await asyncio.gather(*tasks)
        print("Newly generated chapters:", chapters)
        self.state.book.extend(chapters)

        print("Script Scenes", self.state.book)

    @listen(write_chapters)
    async def join_and_save_chapter(self):
        print("Joining and Saving Script")
        # Combine all chapters into a single markdown string
        book_content = ""

        for chapter in self.state.book:
            # Add the chapter title as an H1 heading
            book_content += f"# {chapter.title}\n\n"
            # Add the chapter content
            book_content += f"{chapter.content}\n\n"

        # The title of the book from self.state.title
        book_title = self.state.title

        # Create the filename by replacing spaces with underscores and adding .md extension
        filename = f"./{book_title.replace(' ', '_')}.txt"

        # Save the combined content into the file
        with open(filename, "w", encoding="utf-8") as file:
            file.write(book_content)

        print(f"Book saved as {filename}")


def kickoff():
    poem_flow = PoemFlow()
    poem_flow.kickoff()


def plot():
    poem_flow = PoemFlow()
    poem_flow.plot()


if __name__ == "__main__":
    kickoff()
