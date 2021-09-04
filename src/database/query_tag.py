from .models import Tag

class ReadTag:
    def check_tag_existence(self, course_id):
        return Tag.query.filter(Tag.course_id==course_id).first() is not None
    
    def display_tags(self, queried):
        return [f'{course.course_id} | {course.name}' for course in queried]

    def display_all_tags(self):
        return self.display_tags(Tag.query)

    def display_top_tags(self):
        return self.display_tags(Tag.query.order_by(Tag.count.desc()).limit(10))
    
    def get_tag_from_id(self, tag_id):
        return Tag.query.filter(Tag.id == tag_id).first()

    def tag_lookup(self, course_id):
        tag = Tag.query.filter(Tag.course_id == course_id).first()
        return tag.id if tag is not None else None

    def get_all_tags(self):
        return Tag.query.all()