"""
Management command to create a sample Python learning track.

Creates a complete learning path with:
- Area: Programming
- Topic: Python Basics
- Track: Introduction to Python
- 10 Steps: Mix of lessons and quizzes (Mimo/Duolingo style)

Usage:
    python manage.py seed_python_track
    python manage.py seed_python_track --clear  # Clear existing data first
"""

from django.core.management.base import BaseCommand
from learning.models import Area, Topico, Trilha, Passo, Questao, Alternativa


class Command(BaseCommand):
    help = 'Create a sample Python learning track with 10 exercises'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing Python track before creating',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing Python track...')
            Area.objects.filter(title='Programming').delete()
            self.stdout.write(self.style.SUCCESS('✓ Cleared'))

        self.stdout.write('Creating Python learning track...')

        # ====================================================================
        # Create Area: Programming
        # ====================================================================
        area, created = Area.objects.get_or_create(
            title='Programming',
            defaults={
                'description': 'Learn programming languages and computer science fundamentals',
                'icon': '💻',
                'order': 1
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created Area: {area.title}'))
        else:
            self.stdout.write(self.style.WARNING(f'↻ Area already exists: {area.title}'))

        # ====================================================================
        # Create Topic: Python Basics
        # ====================================================================
        topic, created = Topico.objects.get_or_create(
            area=area,
            title='Python Basics',
            defaults={
                'description': 'Master the fundamentals of Python programming',
                'icon': '🐍',
                'order': 1
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created Topic: {topic.title}'))
        else:
            self.stdout.write(self.style.WARNING(f'↻ Topic already exists: {topic.title}'))

        # ====================================================================
        # Create Track: Introduction to Python
        # ====================================================================
        track, created = Trilha.objects.get_or_create(
            topic=topic,
            title='Introduction to Python',
            defaults={
                'description': 'Start your Python journey with hands-on exercises',
                'icon': '🚀',
                'order': 1,
                'difficulty': 'beginner'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created Track: {track.title}'))
        else:
            self.stdout.write(self.style.WARNING(f'↻ Track already exists: {track.title}'))
            # Clear existing steps if track exists
            track.steps.all().delete()
            self.stdout.write(self.style.WARNING('  Cleared existing steps'))

        # ====================================================================
        # Create 10 Steps (Mimo/Duolingo style)
        # ====================================================================
        steps_data = [
            # Step 1: Lesson - What is Python?
            {
                'title': 'What is Python?',
                'content_type': 'lesson',
                'order': 1,
                'estimated_time': 3,
                'xp_reward': 10,
                'text_content': '''<h2>Welcome to Python! 🐍</h2>

<p>Python is one of the most popular programming languages in the world. It's used by companies like Google, Netflix, and NASA!</p>

<h3>Why learn Python?</h3>
<ul>
  <li><strong>Easy to read:</strong> Python code looks like English</li>
  <li><strong>Versatile:</strong> Web apps, data science, AI, automation</li>
  <li><strong>In-demand:</strong> Top skill for tech jobs</li>
</ul>

<h3>Your first Python code</h3>
<pre><code>print("Hello, World!")</code></pre>

<p>This simple line displays text on the screen. Let's try it!</p>''',
                'code_snippet': 'print("Hello, World!")',
            },

            # Step 2: Quiz - Python Basics
            {
                'title': 'Python Basics Quiz',
                'content_type': 'quiz',
                'order': 2,
                'estimated_time': 2,
                'xp_reward': 10,
                'questions': [
                    {
                        'text': 'What does the print() function do in Python?',
                        'alternatives': [
                            ('Calculates numbers', False, 'print() is for displaying output, not calculations'),
                            ('Displays text on screen', True, 'Correct! print() shows output to the user'),
                            ('Saves files', False, 'print() doesn\'t save files'),
                            ('Deletes variables', False, 'print() only displays output'),
                        ]
                    },
                ]
            },

            # Step 3: Lesson - Variables
            {
                'title': 'Storing Data in Variables',
                'content_type': 'lesson',
                'order': 3,
                'estimated_time': 4,
                'xp_reward': 10,
                'text_content': '''<h2>Variables: Your Data Containers 📦</h2>

<p>Variables store information that your program can use and change.</p>

<h3>Creating Variables</h3>
<pre><code>name = "Alice"
age = 25
is_student = True</code></pre>

<p>Notice:</p>
<ul>
  <li>Use <code>=</code> to assign values</li>
  <li>No need to declare types (Python figures it out!)</li>
  <li>Variable names should be descriptive</li>
</ul>

<h3>Variable Naming Rules</h3>
<ul>
  <li>✅ Use letters, numbers, underscores</li>
  <li>✅ Start with letter or underscore</li>
  <li>❌ No spaces or special characters</li>
  <li>❌ Can't start with numbers</li>
</ul>''',
                'code_snippet': '''name = "Alice"
age = 25
print(name)
print(age)''',
            },

            # Step 4: Quiz - Variables
            {
                'title': 'Variables Quiz',
                'content_type': 'quiz',
                'order': 4,
                'estimated_time': 2,
                'xp_reward': 10,
                'questions': [
                    {
                        'text': 'Which variable name is valid in Python?',
                        'alternatives': [
                            ('my-variable', False, 'Hyphens are not allowed in variable names'),
                            ('2nd_variable', False, 'Variable names cannot start with a number'),
                            ('my_variable', True, 'Correct! This follows Python naming rules'),
                            ('my variable', False, 'Spaces are not allowed in variable names'),
                        ]
                    },
                ]
            },

            # Step 5: Lesson - Numbers and Math
            {
                'title': 'Working with Numbers',
                'content_type': 'lesson',
                'order': 5,
                'estimated_time': 4,
                'xp_reward': 10,
                'text_content': '''<h2>Math in Python 🧮</h2>

<p>Python is great at math! Let's explore basic operations.</p>

<h3>Basic Operators</h3>
<pre><code>addition = 5 + 3        # 8
subtraction = 10 - 4    # 6
multiplication = 6 * 7  # 42
division = 15 / 3       # 5.0
power = 2 ** 3          # 8 (2 to the power of 3)</code></pre>

<h3>Number Types</h3>
<ul>
  <li><strong>Integers (int):</strong> Whole numbers like 42, -5, 0</li>
  <li><strong>Floats (float):</strong> Decimal numbers like 3.14, -0.5</li>
</ul>

<h3>Try It!</h3>
<pre><code>price = 29.99
quantity = 3
total = price * quantity
print(total)  # 89.97</code></pre>''',
                'code_snippet': '''price = 29.99
quantity = 3
total = price * quantity
print(total)''',
            },

            # Step 6: Quiz - Math Operations
            {
                'title': 'Math Operations Quiz',
                'content_type': 'quiz',
                'order': 6,
                'estimated_time': 2,
                'xp_reward': 10,
                'questions': [
                    {
                        'text': 'What is the result of: 10 / 2 in Python?',
                        'alternatives': [
                            ('5', False, 'Close! But division always returns a float'),
                            ('5.0', True, 'Correct! Division (/) always returns a float in Python'),
                            ('"5"', False, 'Division returns a number, not a string'),
                            ('Error', False, 'This is valid Python code'),
                        ]
                    },
                ]
            },

            # Step 7: Lesson - Strings
            {
                'title': 'Text with Strings',
                'content_type': 'lesson',
                'order': 7,
                'estimated_time': 4,
                'xp_reward': 10,
                'text_content': '''<h2>Strings: Working with Text 📝</h2>

<p>Strings are sequences of characters enclosed in quotes.</p>

<h3>Creating Strings</h3>
<pre><code>single = 'Hello'
double = "World"
multi = """Multiple
lines"""</code></pre>

<h3>String Operations</h3>
<pre><code># Concatenation (joining)
greeting = "Hello" + " " + "World"  # "Hello World"

# Repetition
laugh = "Ha" * 3  # "HaHaHa"

# Length
message = "Python is awesome"
length = len(message)  # 17</code></pre>

<h3>String Methods</h3>
<pre><code>text = "python programming"
print(text.upper())      # "PYTHON PROGRAMMING"
print(text.capitalize()) # "Python programming"
print(text.replace("python", "Python"))  # "Python programming"</code></pre>''',
                'code_snippet': '''name = "Alice"
greeting = "Hello, " + name + "!"
print(greeting)
print(len(greeting))''',
            },

            # Step 8: Quiz - Strings
            {
                'title': 'Strings Quiz',
                'content_type': 'quiz',
                'order': 8,
                'estimated_time': 2,
                'xp_reward': 10,
                'questions': [
                    {
                        'text': 'What does "Python" * 2 produce?',
                        'alternatives': [
                            ('"Python2"', False, '* repeats the string, doesn\'t add numbers'),
                            ('"PythonPython"', True, 'Correct! * repeats the string'),
                            ('Error', False, 'String repetition is valid in Python'),
                            ('"Python Python"', False, 'No space is added between repetitions'),
                        ]
                    },
                ]
            },

            # Step 9: Lesson - Lists
            {
                'title': 'Organizing Data with Lists',
                'content_type': 'lesson',
                'order': 9,
                'estimated_time': 5,
                'xp_reward': 10,
                'text_content': '''<h2>Lists: Collections of Items 📋</h2>

<p>Lists store multiple items in a single variable.</p>

<h3>Creating Lists</h3>
<pre><code>fruits = ["apple", "banana", "orange"]
numbers = [1, 2, 3, 4, 5]
mixed = ["text", 42, True, 3.14]</code></pre>

<h3>Accessing Items</h3>
<pre><code>fruits = ["apple", "banana", "orange"]
print(fruits[0])  # "apple" (first item)
print(fruits[1])  # "banana"
print(fruits[-1]) # "orange" (last item)</code></pre>

<h3>List Methods</h3>
<pre><code>fruits = ["apple", "banana"]
fruits.append("orange")    # Add to end
fruits.insert(0, "mango")  # Add at position
fruits.remove("banana")    # Remove item
length = len(fruits)       # Get length</code></pre>

<p><strong>Remember:</strong> Lists start counting from 0!</p>''',
                'code_snippet': '''shopping_list = ["milk", "bread", "eggs"]
shopping_list.append("cheese")
print(shopping_list)
print(len(shopping_list))''',
            },

            # Step 10: Final Quiz
            {
                'title': 'Python Fundamentals - Final Quiz',
                'content_type': 'quiz',
                'order': 10,
                'estimated_time': 3,
                'xp_reward': 20,
                'questions': [
                    {
                        'text': 'What will print(fruits[0]) display if fruits = ["apple", "banana", "orange"]?',
                        'alternatives': [
                            ('banana', False, 'That would be fruits[1]'),
                            ('apple', True, 'Correct! Lists are zero-indexed, so [0] gets the first item'),
                            ('orange', False, 'That would be fruits[2] or fruits[-1]'),
                            ('Error', False, 'This is valid Python code'),
                        ]
                    },
                    {
                        'text': 'Which data type would you use to store someone\'s age?',
                        'alternatives': [
                            ('string', False, 'Age is a number, not text'),
                            ('list', False, 'List is for multiple items'),
                            ('integer', True, 'Correct! Age is a whole number'),
                            ('boolean', False, 'Boolean is True/False'),
                        ]
                    },
                ]
            },
        ]

        # Create each step
        for step_data in steps_data:
            step = Passo.objects.create(
                track=track,
                title=step_data['title'],
                content_type=step_data['content_type'],
                order=step_data['order'],
                estimated_time=step_data['estimated_time'],
                xp_reward=step_data['xp_reward'],
                text_content=step_data.get('text_content', ''),
                code_snippet=step_data.get('code_snippet', ''),
            )

            self.stdout.write(self.style.SUCCESS(f'  ✓ Step {step.order}: {step.title}'))

            # Create questions for quiz steps
            if step.content_type == 'quiz' and 'questions' in step_data:
                for q_data in step_data['questions']:
                    question = Questao.objects.create(
                        step=step,
                        text=q_data['text']
                    )

                    for alt_text, is_correct, explanation in q_data['alternatives']:
                        Alternativa.objects.create(
                            question=question,
                            text=alt_text,
                            is_correct=is_correct,
                            explanation=explanation
                        )

                    self.stdout.write(f'    → Created question with {len(q_data["alternatives"])} alternatives')

        # Summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('✅ Python track created successfully!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write('')
        self.stdout.write(f'Area: {area.title}')
        self.stdout.write(f'Topic: {topic.title}')
        self.stdout.write(f'Track: {track.title}')
        self.stdout.write(f'Steps: {track.steps.count()}')
        self.stdout.write('')
        self.stdout.write('Next steps:')
        self.stdout.write('1. Visit /dashboard to see the track')
        self.stdout.write('2. Click on the track to start learning')
        self.stdout.write('3. Complete exercises page by page (Mimo/Duolingo style)')
