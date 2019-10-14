// Implements a dictionary's functionality

#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "dictionary.h"

// Represents number of children for each node in a trie
#define N 27

// Represents a node in a trie
typedef struct node
{
    bool is_word;
    struct node *children[N];
}
node;

void init(node *n);
int hash(char c);
void trav(int *count, node *n);
void doUnload(node *n);


// Represents a trie
node *root;

// Loads dictionary into memory, returning true if successful else false
bool load(const char *dictionary)
{
    // Initialize trie
    root = malloc(sizeof(node));
    if (root == NULL)
    {
        return false;
    }
    init(root);

    // Open dictionary
    FILE *file = fopen(dictionary, "r");
    if (file == NULL)
    {
        unload();
        return false;
    }

    // Buffer for a word
    char word[LENGTH + 1];

    // Insert words into trie
    while (fscanf(file, "%s", word) != EOF)
    {
        node *n = root;
        for (int i = 0; i < strlen(word); i++)
        {
            int key = hash(word[i]);

            node *next = n->children[key];
            if (next == NULL)
            {
                next = malloc(sizeof(node));
                init(next);
                n->children[key] = next;
            }
            n = next;
        }

        n->is_word = true;
    }

    // Close dictionary
    fclose(file);

    // Indicate success
    return true;
}

// Initializes given node and its children
void init(node *n)
{
    n->is_word = false;
    for (int i = 0; i < N; i++)
    {
        n->children[i] = NULL;
    }
}

// calculates index of node in children
int hash(char c)
{
    int key = c - 'a';
    if (key < 0)
    {
        key = N - 1;
    }
    return key;
}

// Returns number of words in dictionary if loaded else 0 if not yet loaded
unsigned int size(void)
{
    if (root == NULL)
    {
        return 0;
    }
    int count = 0;
    int *pcount = &count;
    trav(pcount, root);
    return *pcount;
}

// Helper func to traverse recursively through trie depth first
void trav(int *count, node *n)
{
    if (n == NULL)
    {
        return;
    }
    if (n->is_word)
    {
        (*count)++;
    }
    for (int i = 0; i < N; i++)
    {
        trav(count, n->children[i]);
    }
}

// Returns true if word is in dictionary else false
bool check(const char *word)
{
    int length = strlen(word);
    if (length > LENGTH + 1 || length == 0)
    {
        return false;
    }

    node *n = root;
    for (int i = 0; i < length; i++)
    {
        char lowerC = tolower(word[i]);
        int key = hash(lowerC);

        node *next = n->children[key];
        if (next == NULL)
        {
            return false;
        }
        n = next;
    }
    return n->is_word;
}

// Unloads dictionary from memory, returning true if successful else false
bool unload(void)
{
    if (root == NULL)
    {
        return false;
    }
    doUnload(root);
    return true;
}

// Helper func to traverse recursively through trie depth first
void doUnload(node *n)
{
    if (n == NULL)
    {
        return;
    }
    for (int i = 0; i < N; i++)
    {
        node *child = n->children[i];
        doUnload(child);
    }
    free(n);
}
