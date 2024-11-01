import streamlit as st

from gmail_client import GmailAnalyzer


def main():
    st.set_page_config(page_title="CleanMail", layout="wide")

    # Title row with refresh button
    title_col, button_col = st.columns([6, 1])
    with title_col:
        st.title("CleanMail")
    with button_col:
        if st.button("🔄 Refresh", use_container_width=True):
            st.session_state.email_data = None
            st.rerun()

    # Sidebar for authentication
    st.sidebar.header("Authentication")

    # Use session state to store email credentials and sender stats
    if "email_address" not in st.session_state:
        st.session_state.email_address = None
    if "app_password" not in st.session_state:
        st.session_state.app_password = None
    if "email_data" not in st.session_state:
        st.session_state.email_data = None

    with st.sidebar:
        st.session_state.email_address = st.text_input(
            "Gmail Address", value=st.session_state.email_address, type="default"
        )
        st.session_state.app_password = st.text_input(
            "Gmail App Password", value=st.session_state.app_password, type="password"
        )
        if st.button("Connect"):
            if st.session_state.email_address and st.session_state.app_password:
                analyzer = GmailAnalyzer(
                    st.session_state.email_address, st.session_state.app_password
                )
                test_conn = analyzer.connect()
                if test_conn:
                    test_conn.logout()
                    st.success("Successfully connected to Gmail!")
                    st.rerun()

    if st.session_state.email_address and st.session_state.app_password:
        analyzer = GmailAnalyzer(
            st.session_state.email_address, st.session_state.app_password
        )
        # Show "Analyze Emails" button only if sender_stats is not populated
        if st.session_state.email_data is None:
            if st.button("Analyze Emails"):
                progress_bar = st.progress(0)
                status_text = st.empty()

                def update_progress(current, total):
                    progress = current / total
                    progress_bar.progress(progress)
                    status_text.text(f"Processing email {current}/{total}")

                st.session_state.email_data = analyzer.get_sender_statistics(
                    progress_callback=update_progress
                )

                progress_bar.empty()
                status_text.empty()
                st.rerun()

        # Always show the grouped view if email_data is present
        if st.session_state.email_data is not None:
            df = st.session_state.email_data

            # Group by sender and create cards
            for index, row in df.iterrows():
                with st.container():
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.subheader(row["Sender Name"], anchor=False)
                        st.caption(row["Email"])

                    with col2:
                        if st.button(
                            f"Delete {row["Count"]} email(s) from this sender",
                            key=f"delete_{index}",
                        ):
                            deleted_emails_count = analyzer.delete_emails_from_sender(
                                row["Email"]
                            )
                            st.toast(
                                f"Deleted {deleted_emails_count} emails from {row['Email']}"
                            )
                            # Remove the row from the DataFrame
                            st.session_state.email_data = df.drop(index).reset_index(
                                drop=True
                            )
                            st.rerun()
                        if row["Unsubscribe Link"]:
                            st.markdown(f"[Unsubscribe]({row['Unsubscribe Link']})")

                    st.divider()

    else:
        st.info("Please authenticate using your Gmail credentials in the sidebar.")
        st.markdown(
            """
        ### Instructions:
        1. Enter your Gmail address
        2. Enter your [Gmail App Password](https://myaccount.google.com/apppasswords)
        3. Select the number of recent emails to analyze
        4. Click Connect to start analyzing your inbox
        
        **Note:** This app requires a Gmail App Password, not your regular Gmail password!
        [Learn how to create an App Password](https://support.google.com/accounts/answer/185833)
        """
        )

    # Add a button to star the repository
    st.sidebar.markdown(
        """
        ---
        ⭐️ [Star this project on GitHub](https://github.com/BharatKalluri/cleanmail)
        
        🔗 [bharatkalluri.com](https://bharatkalluri.com)
        """
    )


if __name__ == "__main__":
    main()
