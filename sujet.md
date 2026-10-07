# Exercice3 — API de catalogue et qualité des jeux de données

## Contexte

Une équipe Data souhaite disposer d'une API REST permettant :

- de référencer des jeux de données ;
- de consulter les jeux de données publiés ;
- d'enregistrer des contrôles qualité ;
- de gérer plusieurs niveaux d'autorisation ;
- d'administrer les rôles des utilisateurs.

L'API doit être réalisée avec :

- **FastAPI**
- **PostgreSQL**
- **SQLAlchemy**
- **bcrypt**
- **JWT**
- configuration sensible dans un fichier `.env`

Aucune structure de projet n'est imposée.  
Vous êtes responsables de l'organisation complète de l'application.

---

## 1. Utilisateurs et authentification

L'API doit permettre :

```text
POST /auth/register
POST /auth/login
```

### Inscription

L'inscription est publique.

Un nouvel utilisateur doit être créé avec le rôle :

```text
viewer
```

L'utilisateur ne doit pas pouvoir choisir lui-même son rôle lors de l'inscription.

Un utilisateur doit contenir au minimum :

```text
id
username
password_hash
role
```

Le mot de passe ne doit jamais être stocké en clair.

### Connexion

Le login doit :

- rechercher l'utilisateur en base ;
- vérifier le mot de passe avec bcrypt ;
- retourner un JWT si les identifiants sont corrects.

Le JWT doit contenir au minimum :

```text
sub
role
iat
exp
```

---

## 2. Rôles

Trois rôles sont attendus :

```text
viewer
analyst
manager
```

### Viewer

Peut :

- consulter les jeux de données publics ;
- consulter les contrôles qualité.

### Analyst

Peut :

- faire tout ce qu'un viewer peut faire ;
- créer un contrôle qualité ;
- modifier un contrôle qualité.

### Manager

Peut :

- faire tout ce qu'un analyst peut faire ;
- créer, modifier et supprimer des jeux de données ;
- supprimer un contrôle qualité ;
- consulter la liste des utilisateurs ;
- modifier le rôle d'un utilisateur.

---

## 3. Jeux de données

L'API doit gérer des jeux de données avec au minimum :

```text
id
name
description
source
format
is_public
```

Exemple :

```json
{
  "name": "Consommation électrique régionale",
  "description": "Consommation annuelle par région",
  "source": "Open Data",
  "format": "CSV",
  "is_public": true
}
```

### Endpoints attendus

```text
GET    /datasets
GET    /datasets/{id}
POST   /datasets
PUT    /datasets/{id}
DELETE /datasets/{id}
```

### Règles d'accès

```text
GET /datasets
GET /datasets/{id}
```

sont publics, mais ils ne doivent exposer que les datasets dont :

```text
is_public = true
```

Les opérations suivantes sont réservées au rôle `manager` :

```text
POST   /datasets
PUT    /datasets/{id}
DELETE /datasets/{id}
```

---

## 4. Contrôles qualité

L'API doit gérer des contrôles qualité liés à un dataset.

Un contrôle qualité doit contenir au minimum :

```text
id
dataset_id
checked_at
score
status
comment
```

Le score doit être compris entre :

```text
0 et 100
```

Le statut doit être limité à des valeurs cohérentes, par exemple :

```text
PASS
WARNING
FAIL
```

### Endpoints attendus

```text
GET    /quality-checks
GET    /quality-checks/{id}
POST   /quality-checks
PUT    /quality-checks/{id}
DELETE /quality-checks/{id}
```

### Règles d'accès

Consultation :

```text
GET /quality-checks
GET /quality-checks/{id}
```

Accessible à tout utilisateur authentifié :

```text
viewer
analyst
manager
```

Création et modification :

```text
POST /quality-checks
PUT  /quality-checks/{id}
```

Accessible à :

```text
analyst
manager
```

Suppression :

```text
DELETE /quality-checks/{id}
```

Accessible uniquement à :

```text
manager
```

---

## 5. Administration des utilisateurs

Prévoir des endpoints permettant à un `manager` de :

```text
GET   /admin/users
PATCH /admin/users/{id}/role
```

Le changement de rôle doit accepter uniquement :

```text
viewer
analyst
manager
```

Un utilisateur non manager doit recevoir une réponse `403`.

---

## 6. Codes HTTP attendus

L'API doit distinguer correctement :

```text
401 Unauthorized
```

pour :

- absence de token ;
- token invalide ;
- token expiré.

Et :

```text
403 Forbidden
```

pour :

- utilisateur authentifié mais rôle insuffisant.

Utiliser également les codes adaptés pour :

```text
404 Not Found
409 Conflict
422 Unprocessable Entity
```

selon les cas rencontrés.


---

## 7. Sécurité attendue

Le projet doit respecter au minimum les principes suivants :

- aucun mot de passe stocké en clair ;
- mots de passe hachés avec bcrypt ;
- aucun secret JWT écrit directement dans le code ;
- configuration sensible dans `.env` ;
- `.env` ignoré par Git ;
- JWT avec expiration ;
- contrôle des rôles côté API ;
- le front ou Swagger ne doit jamais être considéré comme une barrière de sécurité ;
- `password_hash` ne doit jamais être exposé dans une réponse ;
- l'inscription publique ne permet jamais de choisir un rôle privilégié.

---

## 8. Vérifications minimales

Votre API doit permettre de démontrer les scénarios suivants :

1. créer un utilisateur ;
2. vérifier qu'il reçoit le rôle `viewer` ;
3. se connecter et récupérer un JWT ;
4. lire un dataset public sans token ;
5. constater qu'un viewer ne peut pas créer un dataset ;
6. constater qu'un analyst peut créer un contrôle qualité ;
7. constater qu'un analyst ne peut pas supprimer un contrôle qualité ;
8. constater qu'un manager peut tout administrer ;
9. modifier le rôle d'un utilisateur ;
10. constater les réponses `401` et `403` dans les bons cas ;
11. vérifier le fonctionnement CORS depuis la page HTML indépendante.

