*Vision Agent: Automated IC Datasheet Pinout Extractor*

An automated, local AI agent designed to extract precise IC (Integrated Circuit) pinout configurations from PDF datasheets. Powered by LangChain, Ollama and PyMuPDF, this tool leverages multimodal visual reasoning to locate, read and convert schematic diagrams into standardized JSON arrays, saving them directly to an SQLite database.

This project implements a Modular Prompt Architecture, strictly decoupling the agent's Python execution logic ("The Muscle") from its prompt instructions ("The Brain") using Markdown files.
