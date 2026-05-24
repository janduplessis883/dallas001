from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import requests
import streamlit as st


st.set_page_config(
    page_title="Prophetic Vision Builder",
    page_icon="PV",
    layout="wide",
)


@dataclass(frozen=True)
class Question:
    key: str
    label: str
    help: str | None = None
    height: int = 90


@dataclass(frozen=True)
class Section:
    title: str
    intro: str
    questions: tuple[Question, ...]


STYLE_OPTIONS = [
    "Grounded and compassionate",
    "Bold and prophetic",
    "Poetic and visionary",
    "Direct and practical",
    "Spiritual but accessible",
]

VERSION_OPTIONS = [
    "Short daily declaration",
    "One-page prophetic vision",
    "Detailed transformational blueprint",
    "Morning meditation version",
    "Future-self letter",
]

DEFAULT_GROQ_MODEL = "openai/gpt-oss-120b"

GROQ_MODEL_OPTIONS = {
    "openai/gpt-oss-120b": "OpenAI GPT-OSS 120B",
    "openai/gpt-oss-20b": "OpenAI GPT-OSS 20B",
    "llama-3.3-70b-versatile": "Llama 3.3 70B",
    "llama-3.1-8b-instant": "Llama 3.1 8B Instant",
    "groq/compound": "Groq Compound",
    "groq/compound-mini": "Groq Compound Mini",
    "meta-llama/llama-4-scout-17b-16e-instruct": "Llama 4 Scout 17B 16E",
    "qwen/qwen3-32b": "Qwen3 32B",
}

SECTIONS = [
    *[
        Section(
            title=f"Part 1: Pattern or Behavior #{index}",
            intro="Name one pattern or behavior that is not serving you, then complete the reflection prompts for it.",
            questions=(
                Question(f"pattern_{index}", f"Pattern or behavior #{index}", height=70),
                Question(
                    f"pattern_{index}_when_no_longer",
                    "When I no longer...",
                    "What will become possible when this pattern is no longer leading you?",
                ),
                Question(
                    f"pattern_{index}_energy_from",
                    "The energy I previously put into...",
                ),
                Question(
                    f"pattern_{index}_energy_to",
                    "Will now go toward...",
                ),
                Question(
                    f"pattern_{index}_without",
                    "Without this pattern, my relationships will be...",
                ),
            ),
        )
        for index in range(1, 4)
    ],
    Section(
        title="Part 2: Imagining Your Future Self",
        intro="Imagine yourself 6 months to 1 year from now, looking back at today.",
        questions=(
            Question("future_internal_shift", "The most significant internal shift I see in myself is..."),
            Question("future_challenges", "The new way I handle challenges is..."),
            Question("future_self_relationship", "My new relationship with myself shows up as..."),
        ),
    ),
    Section(
        title="Part 3: Identifying Your Highest Self",
        intro="Name the qualities, responses, and relationship to your past that belong to your highest self.",
        questions=(
            Question(
                "highest_qualities",
                "What qualities do you admire in others that you want to see emerge in yourself?",
            ),
            Question(
                "highest_past",
                "How would your relationship with your past change if you were living as your highest self?",
            ),
            Question(
                "highest_challenges",
                "If you were living completely aligned with your highest potential, how would you respond differently to life's challenges?",
            ),
        ),
    ),
    Section(
        title="Part 4: Discovering Your Themes",
        intro="Look for the repeating themes that are emerging from your answers.",
        questions=(
            Question(
                "theme_emotional",
                "Emotional themes: What feelings come up repeatedly when you imagine your future self?",
            ),
            Question(
                "theme_behavioral",
                "Behavioral themes: What new behaviors or practices appear multiple times?",
            ),
            Question(
                "theme_relationship",
                "Relationship patterns: What patterns do you notice in how you want to interact with others?",
            ),
        ),
    ),
    Section(
        title="Part 5: Building Your Vision",
        intro="Use the house metaphor from the worksheet to shape the structure of the vision.",
        questions=(
            Question(
                "vision_foundation",
                "The foundation: The core principles that will guide my new reality are...",
            ),
            Question(
                "vision_walls",
                "The walls: Each day I will strengthen my new reality by...",
            ),
            Question(
                "vision_roof",
                "The roof: My recovery serves a bigger purpose because...",
            ),
        ),
    ),
    Section(
        title="Part 6: Drafting Your Vision Statement",
        intro="Begin with the central statement.",
        questions=(
            Question("vision_statement", '"I am becoming someone who..."', height=130),
        ),
    ),
    Section(
        title="Part 7: Testing Your Vision",
        intro="Notice how the vision lands in your body and your daily life.",
        questions=(
            Question("test_feel", "When I read this vision, I feel..."),
            Question("test_daily", "I can live this vision in my daily life by..."),
            Question("test_growth", "This vision challenges me to grow by..."),
        ),
    ),
    Section(
        title="Part 8: Refining Your Vision",
        intro="Make the vision clearer, more authentic, and more inspiring.",
        questions=(
            Question("refine_specific", "I am changing this part to be more specific..."),
            Question("refine_forced", "This part feels forced because..."),
            Question("refine_revision", "I am revising it to..."),
            Question("refine_inspiring", "I am making this part more inspiring by..."),
        ),
    ),
    Section(
        title="Part 9: Bringing Your Vision To Life",
        intro="Create simple rhythms that help the vision become embodied.",
        questions=(
            Question("life_morning", "Morning connection: How will you connect with your vision each morning?"),
            Question(
                "life_daily",
                "Daily alignment checks: How will you stay aligned with your vision throughout the day?",
            ),
            Question("life_evening", "Evening reflection: How will you end your day reflecting on your vision?"),
        ),
    ),
    Section(
        title="Part 10: Tracking Your Transformation",
        intro="Define how you will notice growth and revisit the vision over time.",
        questions=(
            Question("track_growth", "I notice I am growing when..."),
            Question("track_challenge_from", "My responses to challenges are shifting from..."),
            Question("track_challenge_to", "My responses to challenges are shifting to..."),
            Question("track_dialogue_from", "My internal dialogue has changed from..."),
            Question("track_dialogue_to", "My internal dialogue has changed to..."),
            Question("monthly_alive", "What aspects of my vision feel alive and relevant right now?"),
            Question("monthly_update", "What parts of my vision might need updating to reflect my growth?"),
            Question("monthly_possible", "How has my understanding of what is possible expanded?"),
        ),
    ),
]


def ask_groq(prompt: str, model: str = DEFAULT_GROQ_MODEL) -> str:
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("Add GROQ_API_KEY to `.streamlit/secrets.toml`.")

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a careful, emotionally intelligent writing partner. "
                    "Return polished prophetic vision drafts based only on the user's worksheet responses."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.8,
    }
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "prophetic-vision-builder/1.0",
        },
        json=payload,
        timeout=60,
    )

    try:
        data = response.json()
    except ValueError as error:
        raise RuntimeError(f"Groq returned a non-JSON response: {response.text[:500]}") from error

    if not response.ok:
        detail = data.get("error", {}).get("message") or data.get("message") or response.text
        raise RuntimeError(f"Groq returned an error: {detail}")

    return data["choices"][0]["message"]["content"]


def text_value(key: str) -> str:
    return str(st.session_state.get(key, "")).strip()


def completion_stats(questions: Iterable[Question]) -> tuple[int, int]:
    question_list = list(questions)
    answered = sum(1 for question in question_list if text_value(question.key))
    return answered, len(question_list)


def render_question(question: Question) -> None:
    st.text_area(
        question.label,
        key=question.key,
        help=question.help,
        height=question.height,
        placeholder="Write in your own words...",
    )


def section_markdown(section: Section) -> str:
    lines = [f"## {section.title}", section.intro]
    for question in section.questions:
        answer = text_value(question.key)
        if answer:
            lines.append(f"- {question.label}\n  {answer}")
    return "\n".join(lines)


def build_master_prompt(
    selected_versions: list[str],
    tone: str,
    audience: str,
    extra_guidance: str,
) -> str:
    filled_sections = [
        section_markdown(section)
        for section in SECTIONS
        if any(text_value(question.key) for question in section.questions)
    ]
    versions = "\n".join(f"- {version}" for version in selected_versions)

    guidance = extra_guidance.strip() or "Keep the language emotionally honest, specific, empowering, and grounded."
    audience_line = audience.strip() or "the person who completed this worksheet"

    return f"""You are helping {audience_line} write a prophetic vision for personal transformation.

Create the following versions:
{versions}

Preferred tone: {tone}

Writing guidance:
- Use the user's own language and themes wherever possible.
- Do not invent trauma details or life events that are not provided.
- Write in first person unless a version clearly works better in second person.
- Make the vision feel believable now while still calling the user higher.
- Include concrete daily embodiment where the user supplied it.
- Avoid generic self-help language.
- {guidance}

Source worksheet responses:

{chr(10).join(filled_sections) if filled_sections else "No worksheet responses were provided yet."}

Return the versions with clear headings. End with 3 brief integration prompts the user can reflect on this week.
"""


def render_sidebar() -> tuple[list[str], str, str, str, str]:
    with st.sidebar:
        st.header("Groq Output")
        selected_versions = st.multiselect(
            "Vision versions",
            VERSION_OPTIONS,
            default=[
                "Short daily declaration",
                "One-page prophetic vision",
                "Detailed transformational blueprint",
            ],
        )
        tone = st.selectbox("Tone", STYLE_OPTIONS, index=0)
        model = st.selectbox(
            "Groq model",
            options=list(GROQ_MODEL_OPTIONS.keys()),
            index=list(GROQ_MODEL_OPTIONS.keys()).index(DEFAULT_GROQ_MODEL),
            format_func=lambda model_id: f"{GROQ_MODEL_OPTIONS[model_id]} ({model_id})",
        )
        audience = st.text_input(
            "Who is this for?",
            placeholder="Example: me, a client in recovery, a coaching participant",
        )
        extra_guidance = st.text_area(
            "Extra instructions",
            placeholder="Anything Groq should know about voice, faith language, length, or boundaries.",
            height=120,
        )
        st.caption("Uses `GROQ_API_KEY` from `.streamlit/secrets.toml`.")
    return selected_versions, tone, audience, extra_guidance, model


def main() -> None:
    st.title("Prophetic Vision Builder")
    st.write(
        "Work through the prompts section by section, then generate a master prompt and send it to Groq to turn your answers into several versions of a prophetic vision."
    )

    selected_versions, tone, audience, extra_guidance, model = render_sidebar()

    all_questions = [question for section in SECTIONS for question in section.questions]
    answered, total = completion_stats(all_questions)
    st.progress(answered / total if total else 0, text=f"{answered} of {total} prompts completed")

    tab_questions, tab_prompt, tab_groq = st.tabs(["Questions", "Master Prompt", "Groq Draft"])

    with tab_questions:
        for index, section in enumerate(SECTIONS):
            answered_section, total_section = completion_stats(section.questions)
            expanded = index == 0 or (answered_section > 0 and answered_section < total_section)
            with st.expander(
                f"{section.title} - {answered_section}/{total_section}",
                expanded=expanded,
            ):
                st.write(section.intro)
                for question in section.questions:
                    render_question(question)

    master_prompt = build_master_prompt(
        selected_versions=selected_versions or ["One-page prophetic vision"],
        tone=tone,
        audience=audience,
        extra_guidance=extra_guidance,
    )

    with tab_prompt:
        st.subheader("Master Prompt")
        st.text_area(
            "Copy this into another tool, or use the Groq Draft tab to send it to Groq.",
            value=master_prompt,
            height=620,
        )
        st.download_button(
            "Download prompt",
            data=master_prompt,
            file_name="prophetic_vision_master_prompt.txt",
            mime="text/plain",
        )

    with tab_groq:
        st.subheader("Draft With Groq")
        st.write("Send the generated master prompt to Groq and draft the selected vision versions.")
        if st.button("Ask Groq", type="primary", disabled=answered == 0):
            try:
                with st.spinner("Asking Groq..."):
                    response = ask_groq(master_prompt, model=model)
            except Exception as error:
                st.error(f"Groq call failed: {error}")
            else:
                st.session_state["groq_response"] = response

        if answered == 0:
            st.info("Fill in at least one worksheet prompt before asking Groq.")

        if st.session_state.get("groq_response"):
            st.download_button(
                "Download draft",
                data=st.session_state["groq_response"],
                file_name="prophetic_vision_draft.md",
                mime="text/markdown",
            )
            st.divider()
            st.markdown(st.session_state["groq_response"])


if __name__ == "__main__":
    main()
