import csv
import itertools
import sys

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
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

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
                # print(f"one_gene: {one_gene}, two_genes: {two_genes}, have_trait: {have_trait}")

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
    # raise NotImplementedError
    probability = 1.0
    for person in people:
        # Determine the number of copies of the gene
        num_genes = (
            2 if person in two_genes else
            1 if person in one_gene else
            0
        )

        # Determine if the person has the trait
        has_trait = person in have_trait

        # Calculate the probability based on the number of genes and trait
        # if the person has no parents, use unconditional probabilities
        if people[person]["mother"] is None and people[person]["father"] is None:
            probability *= PROBS["gene"][num_genes] * PROBS["trait"][num_genes][has_trait]
            # If the person has parents, calculate the probability based on their parents
        else:
            # Determine the number of genes for the mother and father
            mother_genes = (
                1 if people[person]["mother"] in one_gene else
                2 if people[person]["mother"] in two_genes else
                0
                )
            
            father_genes = (
                1 if people[person]["father"] in one_gene else
                2 if people[person]["father"] in two_genes else
                0
            )

            # Calculate the probability of inheriting the gene from parents
            if num_genes == 2:
                # if both parents have 0 genes, the child has 2 genes with mutation from both parents
                if mother_genes == 0 and father_genes == 0:
                    probability *=  PROBS["mutation"] * PROBS["mutation"]
                # if one parent has 1 gene and the other has 0 genes, the child got 1 from mutation and 1 without mutation
                elif (mother_genes == 1 and father_genes == 0) or (mother_genes == 0 and father_genes == 1):
                    probability *= 0.5 * (1 - PROBS["mutation"]) * PROBS["mutation"]
                # if both parents have 1 gene, the child has 2 genes without mutation
                elif mother_genes == 1 and father_genes == 1:
                    probability *= 0.5 * (1 - PROBS["mutation"]) * 0.5 * (1 - PROBS["mutation"])
                # if one parent has 2 genes and the other has 0 genes, the child has 1 gene with mutation and 1 without mutation
                elif (mother_genes == 2 and father_genes == 0) or (mother_genes == 0 and father_genes == 2):
                    probability *= (1 - PROBS["mutation"]) * PROBS["mutation"]
                # if both parents have 2 genes, the child get 1 from each parent without mutation
                elif mother_genes == 2 and father_genes == 2:
                    probability *= (1 - PROBS["mutation"]) * (1 - PROBS["mutation"])
                probability *= PROBS["trait"][num_genes][has_trait]
            if num_genes == 1:
                if mother_genes ==  0 and father_genes == 0:
                    ## got one with mutation , the other without mutation
                    probability *= PROBS["mutation"] * (1 - PROBS["mutation"])
                elif (mother_genes == 1 and father_genes == 0) or (mother_genes == 0 and father_genes == 1):
                    # this is a bit complicated
                    # if the parent wih 0 gene does not mutate, then the other parent with 1 gene has to pass the gene AND does not mutate
                    # if the parent with 0 gene mutate, then the other parent with 1 gene either did not pass the gene or pass it but does not mutate
                    probability *= (1 - PROBS["mutation"]) * 0.5 * (1 - PROBS["mutation"])  + PROBS["mutation"] * (0.5 + 0.5 * ( 1 - PROBS["mutation"]))
                elif mother_genes == 1 and father_genes == 1:
                    # if both parents have 1 gene, the child has 1 gene with mutation and 1 without mutation
                    probability *= 0.5 * (1 - PROBS["mutation"]) * 0.5 * (PROBS["mutation"]) * 2 + 0.5 *  (1 - PROBS["mutation"]) * 0.5 * (1 - PROBS["mutation"]) * 2 
                elif (mother_genes == 2 and father_genes == 0) or (mother_genes == 0 and father_genes == 2):
                    probability *= (1 - PROBS["mutation"]) * (1 - PROBS["mutation"]) + PROBS["mutation"] * PROBS["mutation"]
                elif mother_genes == 2 and father_genes == 2:   
                    probability *= (1 -  PROBS["mutation"]) * PROBS["mutation"]
                probability *= PROBS["trait"][num_genes][has_trait]
            if num_genes == 0:
                if mother_genes == 0 and father_genes == 0:
                    probability *= (1 - PROBS["mutation"]) * (1 - PROBS["mutation"])
                elif (mother_genes == 1 and father_genes == 0) or (mother_genes == 0 and father_genes == 1):
                    probability *= 0.5 * (1 -  PROBS["mutation"]) * (1 -  PROBS["mutation"]) + 0.5 * PROBS["mutation"] * (1 -  PROBS["mutation"])
                elif mother_genes == 1 and father_genes == 1:
                    probability *= 0.5 * PROBS["mutation"] * 0.5 * PROBS["mutation"] + 0.5 * (1 - PROBS["mutation"])  * 0.5 * PROBS["mutation"] * 2 + 0.5 * (1 - PROBS["mutation"]) * 0.5 * (1 - PROBS["mutation"]) 
                elif (mother_genes == 2 and father_genes == 0) or (mother_genes == 0 and father_genes == 2):
                    probability *= PROBS["mutation"] * (1 - PROBS["mutation"])
                elif mother_genes == 2 and father_genes == 2:   
                    probability *= PROBS["mutation"] * PROBS["mutation"]
                probability *= PROBS["trait"][num_genes][has_trait]
    return probability
            
            
    


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    # raise NotImplementedError 
    for person in probabilities:
        # Determine the number of copies of the gene
        num_genes = (
            2 if person in two_genes else
            1 if person in one_gene else
            0
        )

        # Determine if the person has the trait
        has_trait = person in have_trait

        # Update the probabilities for the gene and trait distributions
        probabilities[person]["gene"][num_genes] += p
        probabilities[person]["trait"][has_trait] += p
    return probabilities
    


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    # raise NotImplementedError
    for person in probabilities:
        # Normalize gene probabilities
        total_gene = sum(probabilities[person]["gene"].values())
        for num_genes in probabilities[person]["gene"]:
            probabilities[person]["gene"][num_genes] /= total_gene

        # Normalize trait probabilities
        total_trait = sum(probabilities[person]["trait"].values())
        for has_trait in probabilities[person]["trait"]:
            probabilities[person]["trait"][has_trait] /= total_trait


if __name__ == "__main__":
    main()
