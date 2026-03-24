from typing import List, Optional
from app.domain.entities.models import Prompt, Category, Tag, Model, Attachment


class PromptRepository:
    def get_by_id(self, db, prompt_id: str) -> Optional[Prompt]:
        pass

    def get_all(self, db, skip: int = 0, limit: int = 20) -> List[Prompt]:
        pass

    def search(self, db, q: str = None, type: str = None, category_id: str = None, 
               tag_ids: List[str] = None, model_id: str = None, 
               skip: int = 0, limit: int = 20) -> List[Prompt]:
        pass

    def create(self, db, prompt: Prompt) -> Prompt:
        pass

    def update(self, db, prompt: Prompt) -> Prompt:
        pass

    def delete(self, db, prompt_id: str) -> bool:
        pass


class CategoryRepository:
    def get_by_id(self, db, category_id: str) -> Optional[Category]:
        pass

    def get_all(self, db, type: str = None) -> List[Category]:
        pass

    def create(self, db, category: Category) -> Category:
        pass

    def update(self, db, category: Category) -> Category:
        pass

    def delete(self, db, category_id: str) -> bool:
        pass


class TagRepository:
    def get_by_id(self, db, tag_id: str) -> Optional[Tag]:
        pass

    def get_by_name(self, db, name: str) -> Optional[Tag]:
        pass

    def get_all(self, db) -> List[Tag]:
        pass

    def create(self, db, tag: Tag) -> Tag:
        pass

    def update(self, db, tag: Tag) -> Tag:
        pass

    def delete(self, db, tag_id: str) -> bool:
        pass


class ModelRepository:
    def get_by_id(self, db, model_id: str) -> Optional[Model]:
        pass

    def get_all(self, db, type: str = None) -> List[Model]:
        pass

    def create(self, db, model: Model) -> Model:
        pass

    def update(self, db, model: Model) -> Model:
        pass

    def delete(self, db, model_id: str) -> bool:
        pass


class AttachmentRepository:
    def get_by_id(self, db, attachment_id: str) -> Optional[Attachment]:
        pass

    def get_by_prompt(self, db, prompt_id: str) -> List[Attachment]:
        pass

    def create(self, db, attachment: Attachment) -> Attachment:
        pass

    def delete(self, db, attachment_id: str) -> bool:
        pass