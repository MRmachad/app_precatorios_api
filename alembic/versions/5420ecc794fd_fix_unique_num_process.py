"""fix-unique-num-process

Revision ID: 5420ecc794fd
Revises: 5b72edeba560
Create Date: 2024-12-18 08:00:09.908943

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5420ecc794fd'
down_revision: Union[str, None] = '5b72edeba560'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_metaProcesso_NumeroProcessoConsulta', table_name='metaProcesso')
    op.create_index(op.f('ix_metaProcesso_NumeroProcessoConsulta'), 'metaProcesso', ['NumeroProcessoConsulta'], unique=False)
    op.drop_index('ix_processo_NumeroProcessoConsulta', table_name='processo')
    op.create_index(op.f('ix_processo_NumeroProcessoConsulta'), 'processo', ['NumeroProcessoConsulta'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_processo_NumeroProcessoConsulta'), table_name='processo')
    op.create_index('ix_processo_NumeroProcessoConsulta', 'processo', ['NumeroProcessoConsulta'], unique=True)
    op.drop_index(op.f('ix_metaProcesso_NumeroProcessoConsulta'), table_name='metaProcesso')
    op.create_index('ix_metaProcesso_NumeroProcessoConsulta', 'metaProcesso', ['NumeroProcessoConsulta'], unique=True)
    # ### end Alembic commands ###
