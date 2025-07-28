from data_queries import (
    get_top_mutated_genes,
    get_least_mutated_genes,
    get_mutation_count_for_gene,
    get_total_patients,
    get_mutation_types_for_gene,
    get_genes_with_mutation_count_greater_than,
    get_mrna_expression,
)

from llm_handler import query_llm

print("🧬 cBioPortal LUAD Chatbot (LLM-enabled)")
print("Type 'exit' to quit\n")

while True:
    user_input = input("You: ").lower()

    if "exit" in user_input:
        print("Bot: Goodbye!")
        break

    response = query_llm(user_input)

    if not response or "task" not in response:
        print("Bot: Sorry, I didn't understand your question.")
        continue

    task = response.get("task")
    gene = response.get("gene")
    cancer_type = response.get("cancer_type", "LUAD")  

    try:
        if task == "top_mutated_genes":
            n = 10
            for word in user_input.split():
                if word.isdigit():
                    n = int(word)
            top_genes = get_top_mutated_genes(n)
            print(f"Bot: Top {n} mutated genes in LUAD:")
            print(top_genes)

        elif task == "least_mutated_genes":
            n = 10
            for word in user_input.split():
                if word.isdigit():
                    n = int(word)
            genes = get_least_mutated_genes(n)
            print(f"Bot: Least {n} mutated genes in LUAD:")
            print(genes)

        elif task == "total_patients":
            total = get_total_patients()
            print(f"Bot: There are {total} patients in the LUAD dataset.")

        elif task == "gene_mutation_count" and gene:
            count = get_mutation_count_for_gene(gene)
            print(f"Bot: {gene.upper()} has {count} mutations in LUAD.")

        elif task == "mutation_types" and gene:
            types = get_mutation_types_for_gene(gene)
            print(f"Bot: Mutation types for {gene.upper()}:\n{types}")

        elif task == "genes_with_more_than" and "count" in response:
            n = int(response["count"])
            genes = get_genes_with_mutation_count_greater_than(n)
            print(f"Bot: Genes with more than {n} mutations:")
            print(genes)

        elif task == "mrna_expression" and gene:
            result = get_mrna_expression(gene)
            if result is not None:
                print(f"Bot: mRNA expression summary for {gene.upper()}:\n{result}")
            else:
                print("Bot: Gene not found in expression data.")

        else:
            print("Bot: Sorry, task not recognized or incomplete.")
    except Exception as e:
        print(f"Bot: Error while handling task → {e}")
