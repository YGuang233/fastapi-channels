from functools import lru_cache
from pathlib import Path
from typing import Any, List, Union

import material
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.files import File, Files
from mkdocs.structure.nav import Link, Navigation, Section
from mkdocs.structure.pages import Page

non_translated_sections = [  # 不进行翻译的文件和区域
    # "reference/",
    "release-notes.md",
    "dev-people.md",
    "external-links.md",
    "newsletter.md",
    # "management-tasks.md",
    "management.md",
]


@lru_cache  # TODO: 思考这里@lru_cache装饰器有没有必要，感觉可以留下了且没有影响的，因为下面的打印信息是对应启动的文件位置
def get_missing_translation_content(docs_dir: str) -> str:
    docs_dir_path = Path(docs_dir)
    # print('docs_dir_path',docs_dir_path) # E:\...\...\fastapi-channels\docs\en\docs
    missing_translation_path = docs_dir_path / "missing-translation.md"
    if not missing_translation_path.exists():
        # missing_translation_path = docs_dir_path.parent.parent / "missing-translation.md"
        missing_translation_path = (
            docs_dir_path.parent.parent / "zh/docs/missing-translation.md"
        )
    return missing_translation_path.read_text(encoding="utf-8")


@lru_cache
def get_mkdocs_material_langs() -> List[str]:
    material_path = Path(material.__file__).parent
    material_langs_path = material_path / "templates" / "partials" / "languages"
    langs = [file.stem for file in material_langs_path.glob("*.html")]
    return langs


class ZhFile(File):
    pass


def on_config(config: MkDocsConfig, **kwargs: Any) -> MkDocsConfig:
    available_langs = get_mkdocs_material_langs()
    dir_path = Path(config.docs_dir)
    lang = dir_path.parent.name
    if lang in available_langs:
        config.theme["language"] = lang
    if not (config.site_url or "").endswith(f"{lang}/") and lang != "zh":  # "en"
        config.site_url = f"{config.site_url}{lang}/"
    return config


def resolve_file(*, item: str, files: Files, config: MkDocsConfig) -> None:
    item_path = Path(config.docs_dir) / item  # /为拼接路径，相当于path.join()
    if not item_path.is_file():
        zh_src_dir = (Path(config.docs_dir) / "../../zh/docs").resolve()
        # print(zh_src_dir) # E:\...\...\fastapi-channels\docs\zh\docs
        potential_path = zh_src_dir / item
        if potential_path.is_file():
            files.append(
                ZhFile(
                    path=item,
                    src_dir=str(zh_src_dir),
                    dest_dir=config.site_dir,
                    use_directory_urls=config.use_directory_urls,
                )
            )
        print(
            "potential_path", potential_path
        )  # potential_path E:\波\MD笔记\FastAPI\new\fastapi-channels\docs\zh\docs\img\icon-white.svg
    # print("files", files) # 是对象


def resolve_files(*, items: List[Any], files: Files, config: MkDocsConfig) -> None:
    for item in items:
        if isinstance(item, str):
            resolve_file(item=item, files=files, config=config)
        elif isinstance(item, dict):
            assert len(item) == 1
            values = list(item.values())
            if not values:
                continue
            if isinstance(values[0], str):
                resolve_file(item=values[0], files=files, config=config)
            elif isinstance(values[0], list):
                resolve_files(items=values[0], files=files, config=config)
            else:
                raise ValueError(f"Unexpected value: {values}")


def on_files(files: Files, *, config: MkDocsConfig) -> Files:
    resolve_files(items=config.nav or [], files=files, config=config)
    if "logo" in config.theme:
        resolve_file(item=config.theme["logo"], files=files, config=config)
    if "favicon" in config.theme:
        resolve_file(item=config.theme["favicon"], files=files, config=config)
    resolve_files(items=config.extra_css, files=files, config=config)
    resolve_files(items=config.extra_javascript, files=files, config=config)
    return files


def generate_renamed_section_items(
    items: List[Union[Page, Section, Link]], *, config: MkDocsConfig
) -> List[Union[Page, Section, Link]]:
    new_items: List[Union[Page, Section, Link]] = []
    for item in items:
        if isinstance(item, Section):
            new_title = item.title
            new_children = generate_renamed_section_items(item.children, config=config)
            first_child = new_children[0]
            if isinstance(first_child, Page):
                if first_child.file.src_path.endswith("index.md"):
                    # Read the source so that the title is parsed and available
                    # 读取源，以便标题被解析并可用
                    first_child.read_source(config=config)
                    new_title = first_child.title or new_title
            # Creating a new section makes it render it collapsed by default
            # no idea why, so, let's just modify the existing one
            # 创建新部分使其默认情况下呈现折叠
            # 不知道为什么，所以，让我们修改现有的
            # new_section = Section(title=new_title, children=new_children)
            item.title = new_title
            item.children = new_children
            new_items.append(item)
        else:
            new_items.append(item)
    return new_items


def on_nav(
    nav: Navigation, *, config: MkDocsConfig, files: Files, **kwargs: Any
) -> Navigation:
    new_items = generate_renamed_section_items(nav.items, config=config)
    return Navigation(items=new_items, pages=nav.pages)


def on_pre_page(page: Page, *, config: MkDocsConfig, files: Files) -> Page:
    return page


def on_page_markdown(
    markdown: str, *, page: Page, config: MkDocsConfig, files: Files
) -> str:
    if isinstance(page.file, ZhFile):
        for excluded_section in non_translated_sections:
            if page.file.src_path.startswith(excluded_section):
                return markdown
        missing_translation_content = get_missing_translation_content(config.docs_dir)
        header = ""
        body = markdown
        if markdown.startswith("#"):
            header, _, body = markdown.partition("\n\n")
        return f"{header}\n\n{missing_translation_content}\n\n{body}"
    return markdown
