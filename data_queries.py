import mysql.connector
from typing import List

# Database connection config
DB_CONFIG = {
    "host": "localhost",
    "user": "cbio_user",
    "password": "rootpass",    
    "database": "cbio_luad"
}

def _get_conn():
    """Helper: get a new MySQL connection."""
    return mysql.connector.connect(**DB_CONFIG)

def get_top_mutated_genes(n: int) -> List[str]:
    """Return the top n genes by mutation count."""
    cn = _get_conn(); cur = cn.cursor()
    cur.execute("""
        SELECT gene
        FROM mutations
        GROUP BY gene
        ORDER BY COUNT(*) DESC
        LIMIT %s
    """, (n,))
    genes = [row[0] for row in cur.fetchall()]
    cn.close()
    return genes

def get_least_mutated_genes(n: int) -> List[str]:
    """Return the bottom n genes by mutation count."""
    cn = _get_conn(); cur = cn.cursor()
    cur.execute("""
        SELECT gene
        FROM mutations
        GROUP BY gene
        ORDER BY COUNT(*) ASC
        LIMIT %s
    """, (n if n > 0 else 10,))  
    genes = [row[0] for row in cur.fetchall()]
    cn.close()
    return genes

def get_mutation_count_for_gene(gene: str) -> int:
    """Return the number of mutations observed for a specific gene."""
    cn = _get_conn(); cur = cn.cursor()
    cur.execute("""
        SELECT COUNT(*)
        FROM mutations
        WHERE UPPER(gene) = UPPER(%s)
    """, (gene,))
    count = cur.fetchone()[0]
    cn.close()
    return count

def get_genes_with_mutation_count_greater_than(threshold: int) -> List[str]:
    """Return list of genes whose mutation count exceeds the given threshold."""
    cn = _get_conn(); cur = cn.cursor()
    cur.execute("""
        SELECT gene
        FROM mutations
        GROUP BY gene
        HAVING COUNT(*) > %s
    """, (threshold,))
    genes = [row[0] for row in cur.fetchall()]
    cn.close()
    return genes

def get_total_patients() -> int:
    """Return the total number of unique patients in the mutations table."""
    cn = _get_conn(); cur = cn.cursor()
    cur.execute("SELECT COUNT(DISTINCT patient_id) FROM mutations")
    count = cur.fetchone()[0]
    cn.close()
    return count

def get_mutation_types_for_gene(gene: str) -> List[str]:
    """Return the distinct mutation types observed for a given gene."""
    cn = _get_conn(); cur = cn.cursor()
    cur.execute("""
        SELECT DISTINCT mutation_type
        FROM mutations
        WHERE UPPER(gene) = UPPER(%s)
    """, (gene,))
    types = [row[0] for row in cur.fetchall()]
    cn.close()
    return types

def get_mrna_expression(gene: str) -> float:
    """Return the mRNA expression value for a specific gene (first sample)."""
    cn = _get_conn(); cur = cn.cursor()
    cur.execute("""
        SELECT expression_value
        FROM mrna_expression
        WHERE UPPER(gene) = UPPER(%s)
        LIMIT 1
    """, (gene,))
    res = cur.fetchone()
    cn.close()
    if not res:
        raise KeyError(f"No expression data for gene '{gene}'")
    return float(res[0])
def get_average_age_at_diagnosis() -> float:
    """
    Return the average age at diagnosis across all patients.
    """
    cn = _get_conn()
    cur = cn.cursor()
    cur.execute("SELECT AVG(age_at_diagnosis) FROM clinical_patient")
    avg_age = cur.fetchone()[0] or 0.0
    cn.close()
    return float(avg_age)

def get_patient_count_by_stage() -> dict[str, int]:
    """
    Return a dict mapping each tumor_stage to the number of patients.
    """
    cn = _get_conn()
    cur = cn.cursor()
    cur.execute("""
        SELECT tumor_stage, COUNT(*) 
        FROM clinical_patient
        GROUP BY tumor_stage
        ORDER BY tumor_stage
    """)
    dist = {stage: count for stage, count in cur.fetchall()}
    cn.close()
    return dist
