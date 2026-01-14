import csv
import itertools
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    # if len(sys.argv) != 2:
    #     sys.exit("Usage: python heredity.py data.csv")
        
    data_dir = BASE_DIR + "/data/family0.csv"
    people = load_data(data_dir)

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    bio_structure = get_bio_structure(people, one_gene, two_genes, have_trait)
    
    total_probability = 1
    for name, person in people.items():
        # Gene
        gene = bio_structure[name]["gene"]
        father = person["father"]
        mother = person["mother"]
        if mother == None and father == None:
            gene_probability = PROBS["gene"][gene]
        else:
            mutation = PROBS["mutation"]
            gene_herancy_map = {0: mutation, 1: 0.50, 2: 1 - mutation}
            father_gene_probability = gene_herancy_map[bio_structure[father]["gene"]]
            mother_gene_probability = gene_herancy_map[bio_structure[mother]["gene"]]
            
            two_genes = father_gene_probability * mother_gene_probability
            zero_genes = (1 - father_gene_probability) * (1 - mother_gene_probability)
            one_gene = 1 - two_genes - zero_genes
            one_gene_2 = (father_gene_probability * (1 - mother_gene_probability)) + \
           ((1 - father_gene_probability) * mother_gene_probability)
            
            gene_probability_map = {0: zero_genes, 1: one_gene, 2: two_genes}
            
            gene_probability = gene_probability_map[gene]
        
        # Trait
        trait = bio_structure[name]["trait"]
        trait_probability = PROBS["trait"][gene][trait]
        
        # Gene + Trait
        total_probability *= gene_probability * trait_probability
        
    return total_probability

def get_bio_structure(people, one_gene, two_genes, have_trait):
    bio_structure = {
        name: {
            "gene": 0,
            "trait": False,
        } for name in people
    }
    for name in people:
        gene = 0
        if name in two_genes:
            gene = 2
        elif name in one_gene:
            gene = 1
        bio_structure[name]["gene"] = gene
            
        trait = False
        if name in have_trait:
            trait = True
        bio_structure[name]["trait"] = trait
        
    return bio_structure

def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    bio_structure = get_bio_structure(probabilities, one_gene, two_genes, have_trait)
    
    for name, person in probabilities.items():
        gene = bio_structure[name]["gene"]
        trait = bio_structure[name]["trait"]
        
        person["gene"][gene] += p
        person["trait"][trait] += p

def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for name, person in probabilities.items():
        # Gene
        total_gene_value = 0
        for gene, value in person["gene"].items():
            total_gene_value += value
            
        gene_correction = 1 / total_gene_value
        for gene, value in person["gene"].items():
            person["gene"][gene] = value * gene_correction
        
        # Trait
        total_trait_value = 0
        for trait, value in person["trait"].items():
            total_trait_value += value
            
        trait_correction = 1 / total_trait_value
        for trait, value in person["trait"].items():
            person["trait"][trait] = value * trait_correction


if __name__ == "__main__":
    main()