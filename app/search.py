import logging
import numpy as np
from gensim.models import FastText

class SearchModel:
    def __init__(self, db):
        self.model = FastText.load("model/model.bin")
        self.db = db
    
    def vectorize_text(self, text, lower=False):
        logging.info(f"Vectorizing text: {text}")
        if lower:
            text = text.lower()
        vector = np.zeros(self.model.vector_size)
        words = text.split()
        for word in words:
            if word in self.model.wv:
                vector += self.model.wv[word]
        return vector/len(words)

    def get_similarity_vectors(self, vector1, vector2):
        similarity = np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))
        logging.debug(f"Similarity: {similarity}")
        return similarity

    def get_similarity_text(self, text1, text2, lower=False):
        logging.info(f"Getting similarity text for {text1} and {text2}")
        vector1 = self.vectorize_text(text1, lower)
        vector2 = self.vectorize_text(text2, lower)
        return self.get_similarity_vectors(vector1, vector2)

    def get_similar_videos(self, query, max_results=5):
        logging.info(f"Getting top {max_results} similar videos for {query}")
        query_vector = self.vectorize_text(query)
        video_vectors = self.db.get_video_vectors()
        similarities = list()
        for video_vector in video_vectors:
            logging.info(f"Comparing with {video_vector['_id']}")
            similarity = self.get_similarity_vectors(query_vector, video_vector["vector"])
            similarity_pair = (video_vector["_id"], similarity)
            logging.debug(f"Similarity Pair: {similarity_pair}")
            similarities.append(similarity_pair)
        similarities.sort(key=lambda x: x[1], reverse=True)
        result = list()
        for i in range(max_results):
            result.append(self.db.get_video_details_by_id(similarities[i][0]))
        return result
