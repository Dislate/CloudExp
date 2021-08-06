"""v1.01

Revision ID: 260c733e36d6
Revises: 4a5bfe3a3b03
Create Date: 2021-08-03 14:44:08.892398

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '260c733e36d6'
down_revision = 'a6600994bf2f'
branch_labels = None
depends_on = None

# My migrations script
def upgrade():
    op.drop_constraint('parts_ibfk_1', 'parts',
                       type_='foreignkey')
    op.drop_constraint('chapters_ibfk_1', 'chapters',
                       type_='foreignkey')
    op.drop_constraint('tasks_ibfk_1', 'tasks',
                       type_='foreignkey')
    op.drop_constraint('seo_ibfk_1', 'seo',
                       type_='foreignkey')

    op.rename_table("users", "user")
    op.rename_table("languages", "language")
    op.rename_table('parts', 'part')
    op.rename_table('chapters', 'chapter')
    op.rename_table('tasks', 'task')

    op.create_foreign_key('fk_parts_language_ids_languages',
                          'part', 'language',
                          ['language_id'], ['id_language'],
                          ondelete='CASCADE'),
    op.create_foreign_key('fk_chapters_part_ids_parts',
                          'chapter', 'part',
                          ['part_id'], ['id_part'],
                          ondelete='CASCADE'),
    op.create_foreign_key('fk_tasks_chapter_ids_chapters',
                          'task', 'chapter',
                          ['chapter_id'], ['id_chapter'],
                          ondelete='CASCADE'),

    op.create_foreign_key("fk_seos_chapter_ids_chapters",
                          'seo', 'chapter',
                          ['chapter_id'], ['id_chapter'],
                          ondelete='CASCADE')


def downgrade():
    op.drop_constraint('fk_parts_language_ids_languages', 'part',
                       type_='foreignkey')
    op.drop_constraint('fk_chapters_part_ids_parts', 'chapter',
                       type_='foreignkey')
    op.drop_constraint('fk_seos_chapter_ids_chapters', 'seo', type_='foreignkey')
    op.drop_constraint('fk_tasks_chapter_ids_chapters', 'task',
                       type_='foreignkey')
    op.rename_table("user", "users")
    op.rename_table("language", "languages")
    op.rename_table('part', 'parts')
    op.rename_table('chapter', 'chapters')
    op.rename_table('task', 'tasks')
    op.create_foreign_key('parts_ibfk_1',
                          'parts', 'languages',
                          ['language_id'], ['id_language'],
                          ondelete='CASCADE'),
    op.create_foreign_key('chapters_ibfk_1',
                          'chapters', 'parts',
                          ['part_id'], ['id_part'],
                          ondelete='CASCADE'),
    op.create_foreign_key('tasks_ibfk_1',
                          'tasks', 'chapters',
                          ['chapter_id'], ['id_chapter'],
                          ondelete='CASCADE'),
    op.create_foreign_key('seo_ibfk_1',
                          'seo', 'chapters',
                          ['chapter_id'], ['id_chapter'],
                          ondelete='CASCADE')
