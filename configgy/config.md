# 
(map! :leader
      (:prefix ("d" . "treemacs")
       :desc "Focus Treemacs window" "o" #'treemacs-select-window
       :desc "Unselect Treemacs window" "p" #'other-window))

(after! lsp-python-ms
  (setq lsp-python-ms-python-executable-cmd python-shell-interpreter))

(use-package! ellama
  :init
  (setq ellama-language "English")
  (setq ellama-user-nick "")
  (require 'llm-ollama)
  (require 'llm-openai)
  (setq ellama-provider
        (make-llm-openai-compatible
         :url "https://api.deepseek.com/v1/"
         :key "sk-c7288debcb7b47cd89f1dd43ba1dccfb"
         :chat-model "deepseek-chat"))

  (setq ellama-providers
        '(("llama3.1-8b" . (make-llm-ollama
                            :chat-model "llama3.1:8b"
                            :embedding-model "nomic-embed-large"))
          ("deepseek-chat" . (make-llm-openai-compatible
                              :url "https://api.deepseek.com/v1/"
                              :key "sk-c7288debcb7b47cd89f1dd43ba1dccfb"
                              :chat-model "deepseek-chat"))
          ("deepseek-reasoner" . (make-llm-openai-compatible
                                  :url "https://api.deepseek.com/v1/"
                                  :key "sk-c7288debcb7b47cd89f1dd43ba1dccfb"
                                  :chat-model "deepseek-reasoner"))
          )
        )

  (map! :leader
        (:prefix-map ("e" . "Ellama")
                     (:prefix ("c" . "Code")
                      :desc "Code Complete" "c" #'ellama-code-complete
                      :desc "Add Codeblock" "a" #'ellama-code-add
                      :desc "Edit Codeblock" "e" #'ellama-code-edit
                      :desc "Improve Codeblock" "i" #'ellama-code-improve
                      :desc "Generate Code Review" "r" #'ellama-code-review
                      :desc "Generate Commit Message" "m" #'ellama-generate-commit-message
                      )
                     (:prefix ("s" . "Summary/Session")
                      :desc "Summarize" "s" #'ellama-summarize
                      :desc "Summarize Webpage" "w" #'ellama-summarize-webpage
                      :desc "Summarize Killring" "c" #'ellama-summarize-killring
                      :desc "Load Session" "l" #'ellama-load-session
                      :desc "Rename Session" "r" #'ellama-session-rename
                      :desc "Remove Session" "d" #'ellama-session-remove
                      :desc "Switch Session" "a" #'ellama-session-switch
                      )
                     (:prefix ("i" . "Improve")
                      :desc "Improve Wording" "w" #'ellama-improve-wording
                      :desc "Improve Grammar" "g" #'ellama-improve-grammar
                      :desc "Improve Conciseness" "c" #'ellama-improve-conciseness
                      )
                     (:prefix ("m" . "Make")
                      :desc "Make List" "l" #'ellama-make-list
                      :desc "Make Table" "t" #'ellama-make-table
                      :desc "Make Format" "f" #'ellama-make-format
                      )
                     (:prefix ("a" . "Ask/Chat")
                      :desc "Ask About" "a" #'ellama-ask-about
                      :desc "Chat (Ask Interactively)" "i" #'ellama-chat
                      :desc "Ask Line" "l" #'ellama-ask-line
                      :desc "Ask Selection" "s" #'ellama-ask-selection
                      )
                     (:prefix ("t" . "Translate/Text")
                      :desc "Translate Text" "t" #'ellama-translate
                      :desc "Translate Buffer" "b" #'ellama-translate-buffer
                      :desc "Chat Translation Enable" "e" #'ellama-chat-translation-enable
                      :desc "Chat Translation Disable" "d" #'ellama-chat-translation-disable
                      :desc "Text Complete" "c" #'ellama-complete
                      )
                     (:prefix ("d" . "Define")
                      :desc "Define Word" "w" #'ellama-define-word
                      )
                     (:prefix ("x" . "Context")
                      :desc "Add Buffer To Context" "b" #'ellama-context-add-buffer
                      :desc "Add File To Context" "f" #'ellama-context-add-file
                      :desc "Add Selection To Context" "s" #'ellama-context-add-selection
                      :desc "Add Info Node to Context" "i" #'ellama-context-add-info-node
                      )
                     (:prefix ("p" . "Provider")
                      :desc "Select Provider" "s" #'ellama-provider-select
                      )))
  )


