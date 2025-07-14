import os
import json
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import time
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

try:
    import qdrant_client
    from qdrant_client.http.models import Distance, VectorParams, PointStruct, CollectionStatus
    from qdrant_client import QdrantClient
    from qdrant_client.http.exceptions import ResponseHandlingException
except ImportError:
    logging.error("qdrant_client package not installed. Please install it with 'pip install qdrant-client'")
    qdrant_client = None

try:
    import google.generativeai as genai
except ImportError:
    logging.error("google.generativeai package not installed. Please install it with 'pip install google-generativeai'")
    genai = None

from dotenv import load_dotenv
from domain.models.human_agent import HumanAgent
from domain.models.homepage_content import HomepageContent
import uuid

# Configure logger
logger = logging.getLogger(__name__)

class QdrantRepository:
    def __init__(self, collection_name: str = "human_agents"):
        # Load environment variables
        load_dotenv()
        
        # Initialize Google Gemini client
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        if not self.google_api_key:
            raise ValueError("Google API key not found in .env file")
        
        if genai:
            genai.configure(api_key=self.google_api_key)
            self.genai = genai
        else:
            raise ImportError("google.generativeai package is not installed")
        
        # Initialize Qdrant client with timeout settings
        self.qdrant_api_key = os.getenv("QDRANT_API_KEY")
        if not self.qdrant_api_key:
            raise ValueError("Qdrant API key not found in .env file")
        self.qdrant_cloud_url = os.getenv("QDRANT_CLOUD_URL")
        if not self.qdrant_cloud_url:
            raise ValueError("Qdrant cloud URL not found in .env file")
        
        # Initialize client with timeout settings
        self.client = QdrantClient(
            url=self.qdrant_cloud_url,
            api_key=self.qdrant_api_key,
            timeout=30.0  # 30 second timeout
        )
        self.collection_name = collection_name
        self._initialize_collection()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((ResponseHandlingException, httpx.ConnectTimeout)),
        reraise=True
    )
    def _initialize_collection(self):
        """Initialize the Qdrant collection if it doesn't exist."""
        try:
            # Check if collection exists
            try:
                logger.info(f"Checking if collection {self.collection_name} exists...")
                collection_info = self.client.get_collection(collection_name=self.collection_name)
                
                # Verify collection has correct configuration
                vectors_config = collection_info.config.params.vectors
                # Defensive: handle both dict and object cases
                size = None
                distance = None
                on_disk = None
                # Try attribute access first
                if hasattr(vectors_config, 'size') and hasattr(vectors_config, 'distance') and hasattr(vectors_config, 'on_disk'):
                    size = vectors_config.size
                    distance = vectors_config.distance
                    on_disk = vectors_config.on_disk
                # Fallback to dict access
                elif isinstance(vectors_config, dict):
                    size = vectors_config.get('size')
                    distance = vectors_config.get('distance')
                    on_disk = vectors_config.get('on_disk')
                else:
                    logger.warning(f"Unknown vectors_config type: {type(vectors_config)}. Value: {vectors_config}")
                # If any are missing, log and recreate
                if size != 768 or distance != Distance.COSINE or not on_disk:
                    logger.warning(f"Collection {self.collection_name} exists but has incorrect or missing configuration: size={size}, distance={distance}, on_disk={on_disk}. Recreating...")
                    self.client.delete_collection(collection_name=self.collection_name)
                    self._create_collection()
                else:
                    logger.info(f"Collection {self.collection_name} exists with correct configuration")
                
            except Exception as e:
                if "not found" in str(e).lower() or "404" in str(e):
                    logger.info(f"Collection {self.collection_name} does not exist, creating it...")
                    self._create_collection()
                else:
                    logger.warning(f"Unexpected error checking collection: {str(e)}")
                    raise
                
        except Exception as e:
            logger.error(f"Failed to initialize collection: {str(e)}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((ResponseHandlingException, httpx.ConnectTimeout)),
        reraise=True
    )
    def _create_collection(self):
        """Create a new collection with the proper schema."""
        try:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=768,  # Size for Gemini embeddings-001 model
                    distance=Distance.COSINE,
                    on_disk=True
                )
            )
            logger.info(f"Successfully created collection {self.collection_name}")
        except Exception as e:
            if "already exists" in str(e).lower():
                logger.info(f"Collection {self.collection_name} was created by another process")
            else:
                logger.error(f"Failed to create collection: {str(e)}")
                raise

    def create_home_page_content(self, content: str) -> None:
        """
        Create a content for the home page.

        Args:
            content (str): The document content for the homepage.
        """
        try:
            # Ensure content is a valid string and non-empty
            if not isinstance(content, str) or len(content.strip()) == 0:
                raise ValueError("Content must be a non-empty string.")

            # Generate an embedding for the home page content
            embedding = self._generate_homepage_content_embedding(content)

            # Create a point with the embedding and properly formatted payload
            point = PointStruct(
                id=str(uuid.uuid4()),  # Ensure a new ID is generated
                vector=embedding,  # Use vector instead of vectors
                payload={
                    "content": content,
                    "type": "homepage_content",
                    "created_at": datetime.utcnow().isoformat()
                }
            )

            # Insert the point into the collection
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            logger.info(f"Home page content {point.id} created successfully in Qdrant.")
        except Exception as e:
            logger.error(f"Error creating home page content in Qdrant: {e}")
            raise e

    def _generate_homepage_content_embedding(self, content: str) -> list:
        """
        Generate an embedding for the home page content using Google's Gemini model.

        Args:
            content (str): The home page content data.

        Returns:
            list: The embedding vector.
        """
        try:
            # Debugging: Print the content being passed to Gemini
            print(f"Generating embedding for content: {content[:100]}...")  # Only print first 100 chars for readability
            
            # Generate embedding using Google's Embedding API
            embedding_result = self.genai.embed_content(
                model="models/embedding-001",
                content=content,
                task_type="RETRIEVAL_DOCUMENT"
            )
            
            # Extract the embedding values from the response
            if hasattr(embedding_result, 'embedding'):
                embedding = embedding_result.embedding
            elif isinstance(embedding_result, dict) and 'embedding' in embedding_result:
                embedding = embedding_result['embedding']
            elif isinstance(embedding_result, list):
                embedding = embedding_result
            else:
                raise ValueError(f"Unexpected embedding result format: {type(embedding_result)}")
            
            # Debugging: Print the embedding shape to ensure it's being received properly
            print(f"Embedding generated with length: {len(embedding)}")
            
            # Validate embedding size
            if len(embedding) != 768:
                raise ValueError(f"Invalid embedding size: {len(embedding)}. Expected 768.")
            
            return embedding
        except Exception as e:
            print(f"Error generating embedding for home page content: {e}")
            raise e

    def search_homepage_content(self, query: str, top_k: int = 5) -> list:
        """Search for home page content based on a query.
        
        Args:
            query (str): The search query.
            top_k (int): Number of top results to return.
        
        Returns:
            list: A list of matching home page content.
        """
        try:
            # Generate an embedding for the query using Gemini
            query_embedding = self.genai.embed_content(
                model="models/embedding-001",
                content=query.strip(),
                task_type="RETRIEVAL_QUERY"
            )
            
            # Perform a search
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,  # Use the embedding directly
                limit=top_k
            )
            
            # Extract and return the payload of the search results
            results = [hit.payload for hit in search_result]
            return results
        except Exception as e:
            print(f"Error searching homepage content in Qdrant: {e}")
            raise

    def create_agent(self, human_agent: dict) -> None:
        """
        Create a new human agent in the Qdrant collection.

        Args:
            human_agent (dict): The human agent data to create.
        """
        try:
            # Generate an embedding for the human agent profile
            embedding = self._generate_embedding(human_agent)

            # Create a point with the embedding
            point = PointStruct(
                id=human_agent["id"],
                vector=embedding,
                payload=human_agent
            )

            # Insert the point into the collection
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            print(f"Human agent {human_agent['id']} created successfully in Qdrant.")
        except Exception as e:
            print(f"Error creating human agent in Qdrant: {e}")
            raise e

    def _generate_embedding(self, human_agent: dict) -> list:
        """
        Generate an embedding for the human agent profile using Google's Gemini model.

        Args:
            human_agent (dict): The human agent data.

        Returns:
            list: The embedding vector.
        """
        try:
            # Safely extract values with proper type checking
            name = human_agent.get('name', '')
            headline = human_agent.get('headline', '')
            professional_summary = human_agent.get('professional_summary', '')
            
            # Handle experience items safely
            experience_items = []
            for exp in human_agent.get('experience', []):
                if isinstance(exp, dict):
                    experience_items.append(exp.get('title', ''))
                else:
                    experience_items.append(str(exp))
            
            # Handle project items safely
            project_items = []
            for proj in human_agent.get('projects', []):
                if isinstance(proj, dict):
                    project_items.append(proj.get('name', ''))
                else:
                    project_items.append(str(proj))
            
            # Handle education items safely
            education_items = []
            for edu in human_agent.get('education', []):
                if isinstance(edu, dict):
                    education_items.append(edu.get('degree', ''))
                else:
                    education_items.append(str(edu))
            
            # Construct a text representation of the human agent
            text_representation = f"""
            Name: {name}
            Headline: {headline}
            Professional Summary: {professional_summary}
            Experience: {', '.join(experience_items)}
            Projects: {', '.join(project_items)}
            Education: {', '.join(education_items)}
            """
            
            # Generate embedding using Google's Embedding API
            embedding = self.genai.embed_content(
                model="models/embedding-001",
                content=text_representation,
                task_type="RETRIEVAL_DOCUMENT"
            )
            
            return embedding
        except Exception as e:
            print(f"Error generating embedding for human agent: {e}")
            raise e

    def search_human_agents(self, query: str, top_k: int = 5) -> list:
        """
        Search for human agents based on a query.

        Args:
            query (str): The search query.
            top_k (int): Number of top results to return.

        Returns:
            list: A list of matching human agents.
        """
        try:
            # Generate an embedding for the query
            query_embedding = self.genai.embed_content(
                model="models/embedding-001",
                content=query,
                task_type="RETRIEVAL_QUERY"
            )

            # Perform a search
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k
            )

            # Extract and return the payload of the search results
            results = [hit.payload for hit in search_result]
            return results
        except Exception as e:
            print(f"Error searching human agents in Qdrant: {e}")
            raise e

    def create_ai_agent(self, ai_agent: dict) -> None:
        """Create a new AI agent in the Qdrant collection.
        
        Args:
            ai_agent (dict): The AI agent data to create.
        """
        try:
            # Generate AI-specific embedding
            embedding = self._generate_ai_agent_embedding(ai_agent)
            
            # Create a point with the embedding
            point = PointStruct(
                id=str(ai_agent["id"]),  # Ensure ID is a string
                vector=embedding,
                payload=ai_agent  # Full agent data as payload
            )
            
            # Insert the point into the collection
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            logging.info(f"AI agent {ai_agent['id']} created successfully in Qdrant.")
        except Exception as e:
            logging.error(f"Error creating AI agent in Qdrant: {e}")
            raise
    
    def _generate_ai_agent_embedding(self, ai_agent: dict) -> list:
        """Generate an embedding for the AI agent profile using Google's Gemini model.
        
        Args:
            ai_agent (dict): The AI agent data.
        
        Returns:
            list: The embedding vector.
        """
        try:
            # Concatenate relevant fields to create a single text input
            text_input = f"""
            ID: {ai_agent.get('id', '')}
            Role: {ai_agent.get('role', '')}
            Description: {ai_agent.get('description', '')}
            User ID: {ai_agent.get('user_id', '')}
            Goals: {', '.join(ai_agent.get('goals', []))}
            Feedbacks: {', '.join(ai_agent.get('feedbacks', []))}
            KPIs: {', '.join([f"{kpi.get('kpi', '')}: {kpi.get('expected_value', '')}" for kpi in ai_agent.get('kpis', [])])}
            Available APIs: {', '.join(ai_agent.get('available_apis', []))}
            Persona: {ai_agent.get('persona', {}).get('role', '')}| {ai_agent.get('persona', {}).get('description', '')}
            Team ID: {ai_agent.get('team_id', '')}
            Category ID: {ai_agent.get('category_id', '')}
            Skills: {', '.join(ai_agent.get('skills', []))}
            Category: {ai_agent.get('category', '')}
            Tags: {', '.join(ai_agent.get('tags', []))}
            Image: {ai_agent.get('image', '')}
            Traits: {', '.join(ai_agent.get('traits', []))}
            Price: {ai_agent.get('price', '')}
            Rating: {ai_agent.get('rating', '')}
            Created At: {ai_agent.get('created_at', '')}
            Updated At: {ai_agent.get('updated_at', '')}
            """
            # Ensure text_input is a string
            if not isinstance(text_input, str):
                logging.error(f"Text input is not a string: {type(text_input)}")
                raise ValueError("Text input is not a string")
            
            # Generate embedding using Google's Embedding API
            embedding = self.genai.embed_content(
                model="models/embedding-001",
                content=text_input,
                task_type="RETRIEVAL_DOCUMENT"
            )
            return embedding
        except Exception as e:
            logging.error(f"Error generating embedding for AI agent: {e}")
            raise
    
    def search_ai_agents(self, query: str, top_k: int = 5) -> list:
        """Search for AI agents based on a query.
        
        Args:
            query (str): The search query.
            top_k (int): Number of top results to return.
        
        Returns:
            list: A list of matching AI agents.
        """
        try:
            # Generate an embedding for the query
            query_embedding = self.genai.embed_content(
                model="models/embedding-001",
                content=query,
                task_type="RETRIEVAL_QUERY"
            )
            
            # Perform a search
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k
            )
            
            # Extract and return the payload of the search results
            results = [hit.payload for hit in search_result]
            return results
        except Exception as e:
            logging.error(f"Error searching AI agents in Qdrant: {e}")
            raise

    def save_email_context(self, user_id: str, receiver_email: str, email_subject: str, email_body: str, timestamp: datetime):
        """
        Generates embedding and saves the email context (subject, body, metadata)
        as a vector point in Qdrant, associated with a user_id.

        Args:
            user_id: The ID of the user associated with this email context.
            receiver_email: The email address of the receiver.
            email_subject: The subject of the email.
            email_body: The body content of the email.
            timestamp: The timestamp of when the email was processed/saved.
        """
        try:
            # Combine subject and body for a richer embedding context
            content_to_embed = f"Subject: {email_subject}\n\nBody: {email_body}"
            vector = self._generate_email_embedding(content_to_embed)

            # Define the payload - MUST include user_id for filtering
            payload = {
                "user_id": user_id,
                "receiver_email": receiver_email,
                "email_subject": email_subject,
                "email_body": email_body, # Store the original body for retrieval
                "timestamp": timestamp.isoformat() # Store timestamp as ISO string for consistency
            }

            point_id = str(uuid.uuid4()) # Generate a unique ID for the point

            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(id=point_id, vector=vector, payload=payload)
                ],
                wait=True # Optional: wait for operation to complete
            )
            logger.info(f"Saved email context for user {user_id} with point ID {point_id}")

            # Optional: Add logic here or in a separate task to prune old emails if needed
            # self.prune_old_emails_for_user(user_id, max_emails=50)

        except ValueError as ve: # Catch error from embedding generation
            logger.error(f"Skipping save due to invalid content for user {user_id}: {ve}")
        except Exception as e:
            logger.exception(f"Error saving email context vector for user {user_id}: {e}")
            # Depending on requirements, you might want to re-raise the exception
    
    def _generate_email_embedding(self, text_content: str) -> List[float]:
        """
        Generates an embedding for the given email text content using Google's Gemini model.

        Args:
            text_content (str): The text content (e.g., subject + body) to embed.

        Returns:
            list: The embedding vector.
        """
        if not text_content or not isinstance(text_content, str):
             logger.warning("Attempted to generate embedding for empty or invalid text content.")
             raise ValueError("Cannot generate embedding for empty or invalid text content.")

        try:
            # Generate embedding using Google's Embedding API
            embedding = self.genai.embed_content(
                model="models/embedding-001",
                content=text_content,
                task_type="RETRIEVAL_DOCUMENT"
            )
            logger.debug(f"Generated embedding for text: {text_content[:50]}...")
            return embedding
        except Exception as e:
            logger.exception(f"Error generating email embedding: {e}")
            raise

    def search_email_context(self, user_id: str, query_text: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Searches for relevant email context for a specific user based on semantic similarity.

        Args:
            user_id: The ID of the user whose email context to search.
            query_text: The text to search for similarity (e.g., current email subject/body).
            limit: The maximum number of relevant emails to retrieve.

        Returns:
            A list of dictionaries, each containing the payload of a relevant email context point.
            Returns an empty list if no matches are found or an error occurs.
        """
        if not user_id:
            logger.error("Search failed: user_id cannot be empty.")
            return []
        if not query_text:
            logger.warning(f"Search query text is empty for user {user_id}. Returning no results.")
            return []

        try:
            query_vector = self._generate_email_embedding(query_text)

            # --- Crucial Part: Filter by user_id ---
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="user_id", # The field name in your payload
                        match=MatchValue(value=user_id) # The value to match
                    )
                ]
            )

            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=query_filter, # Apply the filter
                limit=limit,
                with_payload=True # Ensure payload is included in the results
            )

            # Extract payloads from scored points and ensure they have the required fields
            results = []
            for hit in search_result:
                payload = hit.payload
                if isinstance(payload, dict) and 'user_id' in payload:
                    results.append(payload)
                else:
                    logger.warning(f"Skipping result with invalid payload format: {payload}")

            logger.info(f"Found {len(results)} relevant email contexts for user {user_id} matching query.")
            return results

        except ValueError as ve: # Catch error from embedding generation
            logger.error(f"Search failed for user {user_id} due to invalid query text: {ve}")
            return []
        except Exception as e:
            logger.exception(f"Error searching email context for user {user_id}: {e}")
            return [] # Return empty list on error

    def get_embeddings(self, text_input):
        """
        Custom implementation of get_embeddings function to generate embeddings using Gemini.
        
        Args:
            text_input (str): The text to generate embeddings for
            
        Returns:
            object: An object with a 'values' attribute containing the embedding vector
        """
        try:
            # Check if genai is available
            if not hasattr(self, 'genai') or self.genai is None:
                logger.warning("Gemini API not available. Returning mock embeddings.")
                # Return mock embeddings (a vector of zeros with expected dimension)
                mock_dimension = 768  # Dimension for Gemini embeddings-001 model
                mock_values = [0.0] * mock_dimension
                return type('EmbeddingResult', (), {'values': mock_values})
            
            # Use the embeddings model to generate the embedding
            embedding_values = self.genai.embed_content(
                model="models/embedding-001",
                content=text_input,
                task_type="RETRIEVAL_DOCUMENT"
            )
            
            # If empty, return mock embeddings
            if not embedding_values:
                logger.warning("Empty embedding returned. Using mock embeddings.")
                mock_dimension = 768  # Dimension for Gemini embeddings-001 model
                embedding_values = [0.0] * mock_dimension
            
            # Create an object with a 'values' attribute to match the expected interface
            class EmbeddingResult:
                def __init__(self, values):
                    self.values = values
            
            return EmbeddingResult(embedding_values)
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            # Return mock embeddings as fallback
            mock_dimension = 768  # Dimension for Gemini embeddings-001 model
            mock_values = [0.0] * mock_dimension
            return type('EmbeddingResult', (), {'values': mock_values})