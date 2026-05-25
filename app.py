from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable

import streamlit as st
from groq import Groq

# Initialize the Groq client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])


# Simple function to get a response from Groq
@st.cache_resource
def ask_groq(prompt: str, model: str = "llama-3.3-70b-versatile"):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=model,
    )

    return chat_completion.choices[0].message.content

st.set_page_config(
    page_title="Prophetic Vision Builder",
    page_icon="PV",
    layout="wide",
)
st.logo('images/logo2.png', size='large')

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
    icon: str = ":material/article:"


STYLE_OPTIONS = [
    "Poetic and visionary",
    "Grounded and compassionate",
    "Bold and prophetic",
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

DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"

GROQ_MODEL_OPTIONS = {
    "llama-3.3-70b-versatile": "Llama 3.3 70B",
    "qwen/qwen3-32b": "Qwen3 32B",
    "groq/compound": "Groq Compound",
}

SECTIONS = [
    *[
        Section(
            title=f"Part 1: **Pattern or Behavior** Question {index}",
            intro="Name one pattern or behavior that is not serving you, then complete the reflection prompts for it.",
            icon=":material/repeat:",
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
        title="Part 2: **Imagining Your Future Self**",
        intro="Imagine yourself 6 months to 1 year from now, looking back at today.",
        icon=":material/visibility:",
        questions=(
            Question("future_internal_shift", "The most significant internal shift I see in myself is..."),
            Question("future_challenges", "The new way I handle challenges is..."),
            Question("future_self_relationship", "My new relationship with myself shows up as..."),
        ),
    ),
    Section(
        title="Part 3: **Identifying Your Highest Self**",
        intro="Name the qualities, responses, and relationship to your past that belong to your highest self.",
        icon=":material/self_improvement:",
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
        title="Part 4: **Discovering Your Themes**",
        intro="Look for the repeating themes that are emerging from your answers.",
        icon=":material/hub:",
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
        title="Part 5: **Building Your Vision**",
        intro="Use the house metaphor from the worksheet to shape the structure of the vision.",
        icon=":material/foundation:",
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
        title="Part 6: **Drafting Your Vision Statement**",
        intro="Begin with the central statement.",
        icon=":material/edit_note:",
        questions=(
            Question("vision_statement", '"I am becoming someone who..."', height=130),
        ),
    ),
    Section(
        title="Part 7: **Testing Your Vision**",
        intro="Notice how the vision lands in your body and your daily life.",
        icon=":material/fact_check:",
        questions=(
            Question("test_feel", "When I read this vision, I feel..."),
            Question("test_daily", "I can live this vision in my daily life by..."),
            Question("test_growth", "This vision challenges me to grow by..."),
        ),
    ),
    Section(
        title="Part 8: **Refining Your Vision**",
        intro="Make the vision clearer, more authentic, and more inspiring.",
        icon=":material/tune:",
        questions=(
            Question("refine_specific", "I am changing this part to be more specific..."),
            Question("refine_forced", "This part feels forced because..."),
            Question("refine_revision", "I am revising it to..."),
            Question("refine_inspiring", "I am making this part more inspiring by..."),
        ),
    ),
    Section(
        title="Part 9: **Bringing Your Vision To Life**",
        intro="Create simple rhythms that help the vision become embodied.",
        icon=":material/wb_sunny:",
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
        title="Part 10: **Tracking Your Transformation**",
        intro="Define how you will notice growth and revisit the vision over time.",
        icon=":material/monitoring:",
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

NEW_VISION_SECTIONS = SECTIONS[:7]
REVIEW_VISION_SECTIONS = SECTIONS[8:]


def ask_grok(prompt: str) -> str:
    """Replace this stub with your Grok API call using st.secrets."""
    raise NotImplementedError(
        "Add your Grok API call here, then return the model response as a string."
    )


def text_value(key: str) -> str:
    return str(st.session_state.get(key, "")).strip()


def remove_thinking_blocks(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE).strip()


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
    model: str,
    sections: list[Section] | tuple[Section, ...],
) -> str:
    filled_sections = [
        section_markdown(section)
        for section in sections
        if any(text_value(question.key) for question in section.questions)
    ]
    versions = "\n".join(f"- {version}" for version in selected_versions)

    guidance = extra_guidance.strip() or "Keep the language emotionally honest, specific, empowering, and grounded."
    audience_line = audience.strip() or "the person who completed this worksheet"
    selected_versions_text = ", ".join(selected_versions)

    return f"""You are Groq, helping {audience_line} write a prophetic vision for personal transformation.

Sidebar settings selected by the user:
- Name / audience: {audience_line}
- Selected LLM model: {model}
- Selected output versions: {selected_versions_text}
- Selected tone: {tone}
- Extra instructions: {guidance}

Create the following versions:
{versions}

Preferred tone: {tone}

Writing guidance:
- Do not include hidden reasoning, chain-of-thought, or <think>...</think> blocks in the response.
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


def build_review_prompt(
    selected_versions: list[str],
    tone: str,
    audience: str,
    extra_guidance: str,
    model: str,
    previous_vision: str,
) -> str:
    filled_sections = [
        section_markdown(section)
        for section in REVIEW_VISION_SECTIONS
        if any(text_value(question.key) for question in section.questions)
    ]
    versions = "\n".join(f"- {version}" for version in selected_versions)

    guidance = extra_guidance.strip() or "Keep the updated vision emotionally honest, specific, empowering, and grounded."
    audience_line = audience.strip() or "the person reviewing this prophetic vision"
    selected_versions_text = ", ".join(selected_versions)

    return f"""You are helping {audience_line} review and update an existing prophetic vision.

Sidebar settings selected by the user:
- Name / audience: {audience_line}
- Selected LLM model: {model}
- Selected output versions: {selected_versions_text}
- Selected tone: {tone}
- Extra instructions: {guidance}

Update the original prophetic vision using the review responses below. Preserve what still feels alive and true, remove or revise what no longer fits, and make the updated vision more aligned with the user's current growth.

Create the following updated versions:
{versions}

Preferred tone: {tone}

Writing guidance:
- Do not include hidden reasoning, chain-of-thought, or <think>...</think> blocks in the response.
- Use the user's original vision as the foundation.
- Use the review responses as the source of truth for what needs to change.
- Do not invent trauma details or life events that are not provided.
- Write in first person unless a version clearly works better in second person.
- Make the update feel like a natural evolution of the original vision.
- Avoid generic self-help language.
- {guidance}

Original prophetic vision:

{previous_vision.strip() if previous_vision.strip() else "No previous vision was provided."}

Review and adjustment responses:

{chr(10).join(filled_sections) if filled_sections else "No review responses were provided yet."}

Return the updated versions with clear headings. End with 3 brief reflection prompts for the next review cycle.
"""


def render_sidebar() -> tuple[list[str], str, str, str, str]:
    with st.sidebar:
        st.header(":material/settings: LLM Settings")
        model = st.selectbox(
            "LLM Model",
            options=list(GROQ_MODEL_OPTIONS.keys()),
            index=list(GROQ_MODEL_OPTIONS.keys()).index(DEFAULT_GROQ_MODEL),
            format_func=lambda model_id: f"{GROQ_MODEL_OPTIONS[model_id]} ({model_id})",
            help="Choose the language model to generate your prophetic vision. Qwen3 32B is a powerful general-purpose model, Groq Compound is optimized for complex reasoning tasks, and Llama 3.3 70B is known for its creativity and nuanced understanding. Feel free to experiment with different models to see which one resonates best with you and produces the most inspiring vision."
        )
        selected_versions = st.multiselect(
            "Vision versions",
            VERSION_OPTIONS,
            default=[
                "Short daily declaration",
                "One-page prophetic vision",
            ],
        )
        tone = st.selectbox("Tone", STYLE_OPTIONS, index=0, help="The overall style and voice of the prophetic vision. Choose the one that resonates most with you. Revise it, and re-generate you vision to align with your current growth and insights.")
        audience = st.text_input(
            "What is your name?",
            placeholder="Enter your name",
        )
        extra_guidance = st.text_area(
            "Extra instructions",
            placeholder="Specify voice, sexual orientation, faith language, length, or boundaries as required",
            height=120,
            help="Use this space to give the model any extra instructions that will help it create a vision that feels authentic and inspiring to you. For example, you can specify a preferred voice, any faith language you want included or excluded, length preferences, or anything else that will help guide the model to create something that really resonates with you.",
        )
        st.caption("`© 2026 Coaching with Dr. Dallas Bragg`")
        st.image('images/logo3.png')
    return selected_versions, tone, audience, extra_guidance, model


def render_sections(sections: list[Section] | tuple[Section, ...]) -> None:
    for index, section in enumerate(sections):
        answered_section, total_section = completion_stats(section.questions)
        expanded = index == 0 or (answered_section > 0 and answered_section < total_section)
        with st.expander(
            f"{section.title} - {answered_section}/{total_section}",
            expanded=expanded,
            icon=section.icon,
        ):
            st.write(section.intro)
            for question in section.questions:
                render_question(question)


def main() -> None:
    st.title(":material/self_improvement: Prophetic Vision Builder")
    st.caption(
        "Work through the prompts section by section, then generate several versions of your prophetic vision by clicking the **Create button** in the last tab."
    )

    selected_versions, tone, audience, extra_guidance, model = render_sidebar()

    current_review_mode = st.session_state.get("review_mode", False)
    output_tab_label = "Update Your Prophetic Vision" if current_review_mode else "Create Your Prophetic Vision"
    tab_questions, tab_prompt, tab_grok = st.tabs(["Questions", "Master Prompt", output_tab_label])

    with tab_questions:
        review_mode = st.toggle(
            "Review or update a previously created prophetic vision",
            value=False,
            key="review_mode",
            help="Turn this on if you already have a prophetic vision and want to test, refine, and update it.",
        )

    active_sections = REVIEW_VISION_SECTIONS if review_mode else NEW_VISION_SECTIONS
    all_questions = [question for section in active_sections for question in section.questions]
    answered, total = completion_stats(all_questions)
    st.progress(answered / total if total else 0, text=f"{answered} of {total} prompts completed")

    with tab_questions:
        if review_mode:
            st.caption("Upload or paste your previous prophetic vision, then answer Parts 7-10 to help the LLM update it with your current growth and needed adjustments.")
            uploaded_vision = st.file_uploader(
                "Upload your previous prophetic vision",
                type=["md", "txt"],
                help="Upload the Markdown or text file you downloaded from a previous session.",
            )
            if uploaded_vision is not None:
                st.session_state["previous_vision_text"] = uploaded_vision.getvalue().decode("utf-8", errors="replace")
            st.text_area(
                "Or paste your previous prophetic vision",
                key="previous_vision_text",
                height=260,
                placeholder="Paste your previously created prophetic vision here...",
            )
            render_sections(REVIEW_VISION_SECTIONS)
        else:
            st.caption("Answer Parts 1-5 to create a new prophetic vision. The more you answer, the richer your prophetic vision will be.")
            render_sections(NEW_VISION_SECTIONS)

    previous_vision = text_value("previous_vision_text")
    if review_mode:
        master_prompt = build_review_prompt(
            selected_versions=selected_versions or ["One-page prophetic vision"],
            tone=tone,
            audience=audience,
            extra_guidance=extra_guidance,
            model=model,
            previous_vision=previous_vision,
        )
        action_label = "Update Prophetic Vision"
        action_icon = ":material/autorenew:"
        spinner_text = "Updating your prophetic vision..."
        response_key = "updated_prophetic_vision_response"
        download_name = "updated_prophetic_vision.md"
    else:
        master_prompt = build_master_prompt(
            selected_versions=selected_versions or ["One-page prophetic vision"],
            tone=tone,
            audience=audience,
            extra_guidance=extra_guidance,
            model=model,
            sections=NEW_VISION_SECTIONS,
        )
        action_label = "Create Prophetic Vision"
        action_icon = ":material/add_notes:"
        spinner_text = "Creating your prophetic vision..."
        response_key = "prophetic_vision_response"
        download_name = "prophetic_vision.md"

    with tab_prompt:
        st.subheader("Master Prompt")
        st.text_area(
            "Review the prompt that will be sent to Groq when you press Create.",
            value=master_prompt,
            height=620,
        )
        st.download_button(
            "Download prompt",
            data=master_prompt,
            file_name="prophetic_vision_master_prompt.txt",
            mime="text/plain",
        )

    with tab_grok:
        st.subheader("Review Your Prophetic Vision" if review_mode else "Create Your Prophetic Vision")
        if review_mode:
            st.write(":shimmer[Update your prophetic vision by clicking the button below.]")
            st.caption("Adjust the setting in the sidebar to give the model extra guidance on how to update your vision, then click the button to generate an updated version of your prophetic vision that reflects your current growth and needed adjustments.")
            if not previous_vision:
                st.success("Upload or paste your previous prophetic vision in the Questions tab before updating it.")
        else:
            st.write(":shimmer[Create your prophetic vision by clicking the button below.]")
            st.caption("Adjust the settings in the sidebar to give the model guidance on how to create your vision, then click the button to generate several versions of your prophetic vision that you can reflect on, share with loved ones, and download for safekeeping.")
        if st.button(
            action_label,
            type="primary",
            icon=action_icon,
            disabled=review_mode and not previous_vision,
        ):
            try:
                with st.spinner(spinner_text):
                    response = ask_groq(master_prompt, model=model)
            except Exception as error:
                st.error(f"Grok call failed: {error}")
            else:
                st.session_state[response_key] = remove_thinking_blocks(response)

        if st.session_state.get(response_key):
            if review_mode:
                st.info("Download your updated prophetic vision so you can upload it again for a future review.")
            else:
                st.info("Download your prophetic vision so you can upload it in the future to adjust or review your vision.")
            st.download_button(
                "Download Markdown",
                data=st.session_state[response_key],
                file_name=download_name,
                mime="text/markdown",
                type="secondary",
                icon=":material/download:",
            )
            st.divider()
            st.markdown(st.session_state[response_key])


if __name__ == "__main__":
    main()
