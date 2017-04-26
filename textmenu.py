import click


def get_colored_enumerated_list(items, num_color='yellow'):
    items.sort()
    padding = len(str(len(items)))
    numbers = (str(i).rjust(padding) for i in range(1, len(items) + 1))
    numbers = (click.style(i, fg=num_color) for i in numbers)
    return (n + ' ' + i for n, i in zip(numbers, items))
