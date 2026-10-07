<?php

namespace LinkCraftor\Runtime;

final class HookRegistry
{
    private array $hooks = [];

    public function action(
        string $hook,
        callable|array|string $callback,
        int $priority = 10,
        int $accepted_args = 1
    ): void {
        $this->hooks[] = [
            'type'          => 'action',
            'hook'          => $hook,
            'callback'      => $callback,
            'priority'      => $priority,
            'accepted_args' => $accepted_args,
        ];

        if ( function_exists( 'add_action' ) ) {
            add_action(
                $hook,
                $callback,
                $priority,
                $accepted_args
            );
        }
    }

    public function filter(
        string $hook,
        callable|array|string $callback,
        int $priority = 10,
        int $accepted_args = 1
    ): void {
        $this->hooks[] = [
            'type'          => 'filter',
            'hook'          => $hook,
            'callback'      => $callback,
            'priority'      => $priority,
            'accepted_args' => $accepted_args,
        ];

        if ( function_exists( 'add_filter' ) ) {
            add_filter(
                $hook,
                $callback,
                $priority,
                $accepted_args
            );
        }
    }

    public function all(): array
    {
        return $this->hooks;
    }
}