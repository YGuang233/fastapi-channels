from typing import Optional

from pydantic import BaseModel


class Person(BaseModel):
    name: str
    age: Optional[int] = None
    email: str
    hobby: list[str]

    def introduce_me(self) -> None:
        print("hello!😀")
        print(
            f"i am {self.name}, {f'{self.age} years old this year' if self.age else '''I won't tell you my age'''}"
        )
        print(f"my email is {self.email}")
        print(f"my hobby: {', '.join(self.hobby)}")


if __name__ == "__main__":
    my = Person(
        name="BXZDYG",
        age=None,
        email="banxingzhedeyangguang@gmail.com",
        hobby=["code", "draw", "sleep", "game"],
    )
    my.introduce_me()
