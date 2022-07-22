# Questions Endpoints:
endpoint: `/question`

### GET

**GET** `/question`

- *auth* : Token
- *Return* : a list of Dictionaries that represent all the Questions created by author of the Token
- example output:
```
{
    "questions": [
        {
            "answer": "123promise",
            "author": "Please helpme_0249",
            "created_on": "Fri, 22 Jul 2022 02:47:29 GMT",
            "id": 1,
            "question": "123What can you keep after giving to someone?"
        },
        {
            "answer": "parrot",
            "author": "Please helpme_0249",
            "created_on": "Fri, 22 Jul 2022 12:55:24 GMT",
            "id": 2,
            "question": "What is bright orange with green on top and sounds like a parrot?"
        }
    ]
}
```


**GET** `/question/all`

- *auth* : Token
- *Return* : a list of Dictionaries that represent all the - Questions created by all authors
- example output:
```
{
    "questions": [
        {
            "answer": "123promise",
            "author": "Biggie Smalls_0250",
            "created_on": "Fri, 22 Jul 2022 02:47:29 GMT",
            "id": 1,
            "question": "123What can you keep after giving to someone?"
        },
        {
            "answer": "parrot",
            "author": "Please helpme_0249",
            "created_on": "Fri, 22 Jul 2022 12:55:24 GMT",
            "id": 2,
            "question": "What is bright orange with green on top and sounds like a parrot?"
        }
    ]
}
```

### POST
**POST** `/question`
- *auth* : Token
- Creates a New Question with the token owner as the author
- *Return* : ```success <id> created``` if successful
- payload : dictionary with Question and Answer 
- example payload:
```
{
    "question":"What is bright orange with green on top and sounds like a parrot?",
    "answer":"parrot"
}
```

### PUT
**PUT** `/question/<id>`
- *auth* : Token
- Edits a Question with the id `<id>` if the token owner is the author of the question
- *Return* : `success` if successful
- payload : dictionary with Question and/or Answer 
- example payload:
    - Request to /question/2
```
{
    "answer":"parrot"
}
```


### DELETE
**DELETE** `/question/<id>`
- *auth* : Token
- Delets a Question with the id `<id>` if the token owner is the author of the question
- *Return* : `success` if successful

- example DELETE endpoint to delete post with id 2:
    ```DELETE https://cae-bootstore.herokuapp.com/question/2```   

