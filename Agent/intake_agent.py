import os
from typing import Optional

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import json
from langchain_classic.chains.summarize import load_summarize_chain
from langchain_classic.document_loaders import PyPDFLoader
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
load_dotenv()

class IntakeAgent:
    """Load a PDF, send it to Groq via LangChain, and return a summary."""

    def __init__(self,model_name: str = "llama-3.1-8b-instant",temperature: float = 0.1,chunk_size: int = 1000,chunk_overlap: int = 100,):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model_name = model_name
        self.temperature = temperature
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.llm = self._build_llm()

    def _build_llm(self):
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is required. Set it or pass api_key to IntakeAgent.")
        return ChatGroq(
            api_key=self.api_key,
            model_name=self.model_name,
            temperature=self.temperature,
        )

    def _load_and_split(self, pdf_path: str):
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        if not documents:
            raise ValueError(f"No text could be loaded from PDF: {pdf_path}")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )
        return text_splitter.split_documents(documents)

    def summarize_pdf(self, pdf_path: str) -> str:
        documents = self._load_and_split(pdf_path)
        summarization_chain = load_summarize_chain(
            self.llm,
            chain_type="map_reduce",
            verbose=False,
        )
        result = summarization_chain.invoke({"input_documents": documents})
        summary = result.get("output_text", str(result))
        return summary.strip()
    
    def get_details_from_pdf(self, pdf_path: str) -> dict:
        """Extract important details from PDF like policy number, claim ID, etc."""
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        if not documents:
            raise ValueError(f"No text could be loaded from PDF: {pdf_path}")
        # Combine all document text
        full_text = "\n".join([doc.page_content for doc in documents])
        # Create extraction prompt
        extraction_prompt = PromptTemplate(
            input_variables=["text"],
            template="""Extract the following details from the document text below. 
                Return the results as JSON format with these fields:
                - policy_number
                - claim_id
                - claimant_name
                - date_of_claim
                - claim_amount
                - claim_type
                - status
                If a field is not found, use null. Only return valid JSON.
                Document Text:
                {text}
                JSON Response:"""
            )
        # Build extraction chain
        extraction_chain = extraction_prompt | self.llm
        response = extraction_chain.invoke({"text": full_text[:3000]})  # Limit text length
        # Parse response
        try:
            if hasattr(response, 'content'):
                json_str = response.content
            else:
                json_str = str(response)
            
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', json_str, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return json.loads(json_str)
        except json.JSONDecodeError:
            return {"error": "Could not parse response as JSON", "raw_response": str(response)}


def summarize_pdf_with_groq(pdf_path: str ) -> str:
    summarizer = IntakeAgent()
    return summarizer.summarize_pdf(pdf_path)


def extract_details_from_pdf(pdf_path: str) -> dict:
    """Extract important details from PDF like policy number, claim ID, etc."""
    extractor = IntakeAgent()
    return extractor.get_details_from_pdf(pdf_path)

if __name__ == "__main__":
    # Build absolute path from script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    pdf_path = os.path.join(project_root, "document", "claimant_1.pdf")
    
    print("=" * 60)
    print("Extracting Details from PDF...")
    print("=" * 60)
    details = extract_details_from_pdf(pdf_path=pdf_path)
    print("Extracted Details:")
    print(json.dumps(details, indent=2))
    
    print("\n" + "=" * 60)
    print("Generating Summary...")
    print("=" * 60)
    summary = summarize_pdf_with_groq(pdf_path=pdf_path)
    print("Summary:")
    print(summary)
