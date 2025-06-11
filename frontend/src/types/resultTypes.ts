export type CharacterInfo = {
  char: string;
  korean_gloss: string;
  pinyin: string;
  english_gloss: string;
};

export type WordInfo = {
  korean: string;
  hanja: string;
  characters: CharacterInfo[];
};

export type ExampleInfo = {
  sentence: string;
  translation: string;
};

export type ResultType = {
  koreanDef: string;
  sentenceGloss: string;
  romanized: string;
  example?: ExampleInfo;
  words?: WordInfo[];
};
