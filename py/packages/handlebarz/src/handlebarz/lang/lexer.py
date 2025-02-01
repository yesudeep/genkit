# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

# # Handlebars Lexer Implementation
# This file implements a lexical analyzer for Handlebars templates using Python's SLY library.
# It's based on the original Handlebars lexer written in Lex/Flex format.
#
# Original Lex Header:
# ```lex
# %x mu emu com raw escl
#
# %{
# function strip(start, end) {
#   return yytext = yytext.substring(start, yyleng - end + start);
# }
# %}
# ```

from sly import Lexer


class HandlebarsLexer(Lexer):
    # # Token Definitions and States
    # Define all possible tokens that can be produced by the lexer.
    # The original lexer defines these implicitly through its rules.

    tokens = {
        CONTENT,
        ID,
        STRING,
        NUMBER,
        BOOLEAN,
        NULL,
        UNDEFINED,
        OPEN_SEXPR,
        CLOSE_SEXPR,
        OPEN_ARRAY,
        CLOSE_ARRAY,
        OPEN_BLOCK,
        OPEN_ENDBLOCK,
        OPEN_INVERSE,
        OPEN_UNESCAPED,
        CLOSE_UNESCAPED,
        CLOSE,
        EQUALS,
        SEP,
        OPEN_BLOCK_PARAMS,
        CLOSE_BLOCK_PARAMS,
        OPEN_PARTIAL,
        OPEN_PARTIAL_BLOCK,
        DATA,
        PRIVATE_SEP,
        INVERSE,
        COMMENT,
        OPEN_RAW_BLOCK,
        CLOSE_RAW_BLOCK,
        END_RAW_BLOCK,
        OPEN,
    }

    # Whitespace handling
    ignore = ' \t'

    # # State Definitions
    # Original Lex states:
    # ```lex
    # %x mu emu com raw escl
    # ```
    states = {
        'mu': 'exclusive',  # Mustache state - inside {{ }}
        'emu': 'exclusive',  # Escaped Mustache state
        'raw': 'exclusive',  # Raw content state
        'com': 'exclusive',  # Comment state
        'escl': 'exclusive',  # Escaped literal state
    }

    # # Regular Expression Constants
    # Original Lex definitions:
    # ```lex
    # LEFT_STRIP    "~"
    # RIGHT_STRIP   "~"
    # LOOKAHEAD     [=~}\s\/.)\]|]
    # LITERAL_LOOKAHEAD [~}\s)\]]
    # ```
    LEFT_STRIP = r'~'
    RIGHT_STRIP = r'~'
    LOOKAHEAD = r'[=~}\s\/.)\]|]'
    LITERAL_LOOKAHEAD = r'[~}\s)\]]'

    # # ID Character Set
    # Original Lex definition:
    # ```lex
    # ID    [^\s!"#%-,\.\/;->@\[-\^`\{-~]+/{LOOKAHEAD}
    # ```
    ID_CHARS = r'[^\s!"#%-,\.\/;->@\[-\^`\{-~]+'

    # # Initial State Rules
    # Original Lex rule:
    # ```lex
    # [^\x00]*?/("{{") {
    #    if(yytext.slice(-2) === "\\\\") {
    #      strip(0,1);
    #      this.begin("mu");
    #    } else if(yytext.slice(-1) === "\\") {
    #      strip(0,1);
    #      this.begin("emu");
    #    } else {
    #      this.begin("mu");
    #    }
    #    if(yytext) return 'CONTENT';
    # }
    # ```
    @_(r'[^\x00]*?(?={{)')
    def INITIAL_CONTENT(self, t):
        if t.value.endswith('\\\\'):
            t.value = t.value[:-1]
            self.begin('mu')
        elif t.value.endswith('\\'):
            t.value = t.value[:-1]
            self.begin('emu')
        else:
            self.begin('mu')
        if t.value:
            t.type = 'CONTENT'
            return t

    # Original Lex rule:
    # ```lex
    # [^\x00]+  return 'CONTENT';
    # ```
    @_(r'[^\x00]+')
    def CONTENT(self, t):
        return t

    # # EMU State Rules
    # Original Lex rule:
    # ```lex
    # <emu>[^\x00]{2,}?/("{{"|"\\{{"|"\\\\{{"|<<EOF>>) {
    #    this.popState();
    #    return 'CONTENT';
    # }
    # ```
    @_(r'[^\x00]{2,}?(?={{|\\{{|\\\\{{|$)', states=['emu'])
    def EMU_CONTENT(self, t):
        self.pop_state()
        t.type = 'CONTENT'
        return t

    # # Raw State Rules
    # Original Lex rules:
    # ```lex
    # <raw>"{{{{"/[^/]                 this.begin('raw'); return 'CONTENT';
    # ```
    @_(r'{{{{(?![/])', states=['raw'])
    def RAW_OPEN(self, t):
        self.push_state('raw')
        t.type = 'CONTENT'
        return t

    # ```lex
    # <raw>"{{{{/"[^\s!"#%-,\.\/;->@\[-\^`\{-~]+/[=}\s\/.]"}}}}" {
    #   this.popState();
    #   if (this.conditionStack[this.conditionStack.length-1] === 'raw') {
    #     return 'CONTENT';
    #   } else {
    #     strip(5, 9);
    #     return 'END_RAW_BLOCK';
    #   }
    # }
    # ```
    @_(rf'{{{{/({ID_CHARS})/[=}}\s\/.]}}}}', states=['raw'])
    def RAW_CLOSE(self, t):
        self.pop_state()
        if self.current_state() == 'raw':
            t.type = 'CONTENT'
        else:
            t.value = t.value[5:-9]
            t.type = 'END_RAW_BLOCK'
        return t

    # ```lex
    # <raw>[^\x00]+?/("{{{{")          { return 'CONTENT'; }
    # ```
    @_(r'[^\x00]+?(?={{{{)', states=['raw'])
    def RAW_CONTENT(self, t):
        t.type = 'CONTENT'
        return t

    # # Comment State Rules
    # Original Lex rule:
    # ```lex
    # <com>[\s\S]*?"--"{RIGHT_STRIP}?"}}" {
    #   this.popState();
    #   return 'COMMENT';
    # }
    # ```
    @_(r'[\s\S]*?--~?}}', states=['com'])
    def COMMENT_CONTENT(self, t):
        self.pop_state()
        return t

    # # Mustache (mu) State Rules
    # Original Lex rules for various mustache syntax elements
    # ```lex
    # <mu>"("                          return 'OPEN_SEXPR';
    # ```
    @_(r'\(', states=['mu'])
    def OPEN_SEXPR(self, t):
        return t

    @_(r'\)', states=['mu'])
    def CLOSE_SEXPR(self, t):
        return t

    # ```lex
    # <mu>"[" {
    #   if (yy.syntax.square === 'string') {
    #     this.unput(yytext);
    #     this.begin('escl');
    #   } else {
    #     return 'OPEN_ARRAY';
    #   }
    # }
    # ```
    @_(r'\[', states=['mu'])
    def OPEN_ARRAY(self, t):
        # Note: Simplified version - syntax checking would need to be added
        return t

    @_(r'\]', states=['mu'])
    def CLOSE_ARRAY(self, t):
        return t

    # Raw block handling
    @_(r'{{{{', states=['mu'])
    def OPEN_RAW_BLOCK(self, t):
        return t

    @_(r'}}}}', states=['mu'])
    def CLOSE_RAW_BLOCK(self, t):
        self.pop_state()
        self.begin('raw')
        return t

    # Partial and block handling
    @_(r'{{~?>', states=['mu'])
    def OPEN_PARTIAL(self, t):
        return t

    @_(r'{{~?#>', states=['mu'])
    def OPEN_PARTIAL_BLOCK(self, t):
        return t

    @_(r'{{~?#\*?', states=['mu'])
    def OPEN_BLOCK(self, t):
        return t

    @_(r'{{~?/', states=['mu'])
    def OPEN_ENDBLOCK(self, t):
        return t

    # Inverse section handling
    @_(r'{{~?\^\s*~?}}', states=['mu'])
    def INVERSE(self, t):
        self.pop_state()
        return t

    @_(r'{{~?\s*else\s*~?}}', states=['mu'])
    def INVERSE_ELSE(self, t):
        self.pop_state()
        t.type = 'INVERSE'
        return t

    @_(r'{{~?\^', states=['mu'])
    def OPEN_INVERSE(self, t):
        return t

    @_(r'{{~?\s*else', states=['mu'])
    def OPEN_INVERSE_CHAIN(self, t):
        return t

    # Unescaped variable handling
    @_(r'{{~?{', states=['mu'])
    def OPEN_UNESCAPED(self, t):
        return t

    @_(r'{{~?&', states=['mu'])
    def OPEN(self, t):
        return t

    # Comment handling
    @_(r'{{~?!--', states=['mu'])
    def COMMENT_OPEN(self, t):
        self.pop_state()
        self.begin('com')

    @_(r'{{~?!\s*[\s\S]*?}}', states=['mu'])
    def COMMENT_INLINE(self, t):
        self.pop_state()
        t.type = 'COMMENT'
        return t

    # Basic opening mustache
    @_(r'{{~?\*?', states=['mu'])
    def OPEN_BASIC(self, t):
        t.type = 'OPEN'
        return t

    # Various operators and separators
    @_(r'=', states=['mu'])
    def EQUALS(self, t):
        return t

    @_(r'\.\.', states=['mu'])
    def PARENT_ID(self, t):
        t.type = 'ID'
        return t

    @_(rf'\.(?={LOOKAHEAD})', states=['mu'])
    def DOT_ID(self, t):
        t.type = 'ID'
        return t

    @_(r'\.#', states=['mu'])
    def PRIVATE_SEP(self, t):
        return t

    @_(r'[\/.]', states=['mu'])
    def SEP(self, t):
        return t

    # Closing mustaches
    @_(r'}~?}}', states=['mu'])
    def CLOSE_UNESCAPED(self, t):
        self.pop_state()
        return t

    @_(r'~?}}', states=['mu'])
    def CLOSE(self, t):
        self.pop_state()
        return t

    # String literals
    @_(r'"(?:\\["]|[^"])*"', states=['mu'])
    def STRING_DOUBLE(self, t):
        t.value = t.value[1:-1].replace('\\"', '"')
        t.type = 'STRING'
        return t

    @_(r"'(?:\\[']|[^'])*'", states=['mu'])
    def STRING_SINGLE(self, t):
        t.value = t.value[1:-1].replace("\\'", "'")
        t.type = 'STRING'
        return t

    # Data reference
    @_(r'@', states=['mu'])
    def DATA(self, t):
        return t

    # Literals
    @_(rf'true(?={LITERAL_LOOKAHEAD})', states=['mu'])
    def BOOLEAN_TRUE(self, t):
        t.type = 'BOOLEAN'
        return t

    @_(rf'false(?={LITERAL_LOOKAHEAD})', states=['mu'])
    def BOOLEAN_FALSE(self, t):
        t.type = 'BOOLEAN'
        return t

    @_(rf'undefined(?={LITERAL_LOOKAHEAD})', states=['mu'])
    def UNDEFINED(self, t):
        return t

    @_(rf'null(?={LITERAL_LOOKAHEAD})', states=['mu'])
    def NULL(self, t):
        return t

    # Numbers
    @_(rf'-?[0-9]+(?:\.[0-9]+)?(?={LITERAL_LOOKAHEAD})', states=['mu'])
    def NUMBER(self, t):
        return t

    # Block parameters
    @_(r'as\s+\|', states=['mu'])
    def OPEN_BLOCK_PARAMS(self, t):
        return t

    @_(r'\|', states=['mu'])
    def CLOSE_BLOCK_PARAMS(self, t):
        return t

    # Identifiers
    @_(rf'{ID_CHARS}(?={LOOKAHEAD})', states=['mu'])
    def ID(self, t):
        return t

    # # Escaped Literal State Rules
    # Original Lex rule:
    # ```lex
    # <escl>'['('\\]'|[^\]])*']' {
    #   yytext = yytext.replace(/\\([\\\]])/g,'$1');
    #   this.popState();
    #   return 'ID';
    # }
    # ```
    @_(r'\[(?:\\[\\\]]|[^\]])*\]', states=['escl'])
    def ESCL_ID(self, t):
        t.value = t.value.replace(r'\]', ']').replace(r'\\', '\\')
        self.pop_state()
        t.type = 'ID'
        return t

    # Error handling
    def error(self, t):
        print(f"Illegal character '{t.value[0]}'")
        self.index += 1


# # Example Usage
if __name__ == '__main__':
    # Create a lexer instance
    lexer = HandlebarsLexer()

    # Test input
    data = """
    <div class="entry">
      {{#if title}}
        <h1>{{title}}</h1>
        <div class="body">
          {{body}}
        </div>
      {{/if}}
    </div>
    """

    # Tokenize and print results
    for tok in lexer.tokenize(data):
        print(f'Token: {tok.type}, Value: {tok.value}')
