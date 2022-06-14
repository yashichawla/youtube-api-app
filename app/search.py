import logging
import numpy as np
from gensim.models import FastText


class SearchModel:
    def __init__(self, db):
        """
        Load the fastText model and initialize the database connection object
        """
        self.model = FastText.load("model/model.bin")
        self.db = db

    def vectorize_text(self, text, lower=False):
        """
        Given a text, return the average word embedding vector for the text
        """
        logging.info(f"Vectorizing text: {text}")
        if lower:
            text = text.lower()

        # assign a zero vector
        vector = np.zeros(self.model.vector_size)

        # split text into words
        words = text.split()

        for word in words:
            # add the word vector to the total vector
            if word in self.model.wv:
                vector += self.model.wv[word]

        # divide by the number of words
        return vector / len(words)

    def get_similarity_vectors(self, vector1, vector2):
        """
        Find the dot product of two vectors
        """
        similarity = np.dot(vector1, vector2) / (
            np.linalg.norm(vector1) * np.linalg.norm(vector2)
        )
        logging.debug(f"Similarity: {similarity}")
        return similarity

    def get_similarity_text(self, text1, text2, lower=False):
        """
        Find the similarity between two texts by finding the dot product of their vectors
        """
        logging.info(f"Getting similarity text for {text1} and {text2}")
        vector1 = self.vectorize_text(text1, lower)
        vector2 = self.vectorize_text(text2, lower)
        return self.get_similarity_vectors(vector1, vector2)

    def get_similar_videos(self, query, max_results=5):
        """
        Find the videos that are most similar to the query text
        """
        logging.info(f"Getting top {max_results} similar videos for {query}")

        # vectorize the query text
        query_vector = self.vectorize_text(query)

        # obtain all the video vectors from the database
        video_vectors = self.db.get_video_vectors()
        similarities = list()
        for video_vector in video_vectors:
            logging.info(f"Comparing with {video_vector['_id']}")

            # find the similarity between the query vector and the video vector
            similarity = self.get_similarity_vectors(
                query_vector, video_vector["vector"]
            )
            similarity_pair = (video_vector["_id"], similarity)
            logging.debug(f"Similarity Pair: {similarity_pair}")
            similarities.append(similarity_pair)

        # sort the similarities by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)

        # obtain the top max_results similarities
        similarities = similarities[:max_results]
        result = list()
        if similarities:
            for idx, similarity_pair in enumerate(similarities):
                # get the video details from the database
                result.append(self.db.get_video_details_by_id(similarities[idx][0]))
        return result
