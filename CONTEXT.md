# Portfolio Generator

A self-serve web app where a person signs up, fills in one profile, and
publishes one or more public portfolio pages, each with its own set of
projects.

## Language

**Account**:
The identity a person signs in with. Holds the sign-in email, a password hash,
and the owner's Profile. An Account owns zero or more Portfolios.
_Avoid_: User, login

**Profile**:
The personal details attached to an Account and shown at the top of every one
of its Portfolios: display name, age, contact email, GitHub link, phone. The
contact email is a separate field from the sign-in email.
_Avoid_: Bio, about, user info

**Portfolio**:
A public page owned by exactly one Account, identified in its URL by its own
id, containing an owner-chosen title and a list of Projects. Always public;
there is no draft state. An Account may own several, distinguished only by
their title.
_Avoid_: CV, page, site

**Project**:
One item within a Portfolio: name, description, image, link, and a skill list.
Belongs to exactly one Portfolio.
_Avoid_: Work, entry

**Skill list**:
The set of short skill tags displayed on a Project.
_Avoid_: dotlist, tags, keywords
